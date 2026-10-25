"""Per-user OS credential storage for locally enrolled Rezon workers.

Secrets are never written to project files, shell arguments or diagnostics.
Windows: Credential Manager. Linux: Secret Service (secret-tool).
Unsupported or unavailable stores fail closed.
"""
from __future__ import annotations

import subprocess
import sys


class CredentialError(ValueError):
    pass


ROLES = frozenset(("lappy", "vn1", "vn2", "malaphor"))


def validate_role(role: str) -> str:
    if type(role) is not str or role not in ROLES:
        raise CredentialError("invalid worker identity")
    return role


def validate_token(token: str) -> str:
    if type(token) is not str or not 16 <= len(token) <= 256 or (
        not token.isascii() or not token.isprintable()
        or any(c.isspace() for c in token)
    ):
        raise CredentialError("invalid worker credential")
    return token


def _python_service() -> object:
    """Use the existing user keyring without needing system package privileges."""
    try:
        import secretstorage
        return secretstorage
    except ImportError:
        raise CredentialError("Python Secret Service client unavailable") from None


def _item_path(item: object) -> str:
    """Secret Service item identity, not credential content."""
    path = getattr(item, "item_path", None)
    if not isinstance(path, str) or not path:
        raise CredentialError("local Secret Service item identity unavailable")
    return path


def _python_linux_save(role: str, token: str) -> None:
    service = _python_service()
    attributes = {"service": "rezon-tkik", "role": role}
    try:
        bus = service.dbus_init()
        collection = service.get_default_collection(bus)
        if collection.is_locked():
            raise CredentialError("local keyring is locked")

        # A collection's replace=True affects only that collection, while the
        # role lookup spans *all* collections. Refuse ambiguous storage before
        # writing, and do not edit another collection's entries.
        global_items = list(service.search_items(bus, attributes))
        default_items = list(collection.search_items(attributes))
        if len(global_items) != len(default_items) or len(global_items) > 1:
            raise CredentialError("conflicting local worker credential")
        if global_items and (
            _item_path(global_items[0]) != _item_path(default_items[0])
            or global_items[0].is_locked()
            or default_items[0].is_locked()
        ):
            raise CredentialError("conflicting local worker credential")

        created = collection.create_item(
            "Rezon worker " + role, attributes, token.encode("ascii"),
            replace=True,
        )

        # Re-check global uniqueness after the write: another collection may
        # have acquired the same role during the operation. Failure may leave
        # our local item saved, but MUST never report enrollment success.
        items = list(service.search_items(bus, attributes))
        if (len(items) != 1 or items[0].is_locked()
                or _item_path(items[0]) != _item_path(created)):
            raise CredentialError("worker credential storage is ambiguous")
    except CredentialError:
        raise
    except Exception:
        raise CredentialError("local Secret Service could not store credential") from None


def _python_linux_load(role: str) -> str:
    service = _python_service()
    try:
        bus = service.dbus_init()
        matches = list(service.search_items(
            bus, {"service": "rezon-tkik", "role": role},
        ))
        if len(matches) != 1 or matches[0].is_locked():
            raise CredentialError("no single unlocked role credential found")
        secret = matches[0].get_secret().decode("ascii")
    except CredentialError:
        raise
    except Exception:
        raise CredentialError("local Secret Service could not read credential") from None
    return validate_token(secret)


def _linux_save(role: str, token: str) -> None:
    try:
        r = subprocess.run(
            ["secret-tool", "store", "--label=Rezon worker " + role,
             "service", "rezon-tkik", "role", role],
            input=token + "\n", capture_output=True, text=True, timeout=25,
            check=False,
        )
    except FileNotFoundError:
        _python_linux_save(role, token)
        return
    except (OSError, subprocess.TimeoutExpired):
        raise CredentialError("local Secret Service unavailable") from None
    if r.returncode:
        raise CredentialError("local Secret Service could not store credential")


def _linux_load(role: str) -> str:
    try:
        r = subprocess.run(
            ["secret-tool", "lookup", "service", "rezon-tkik", "role", role],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except FileNotFoundError:
        return _python_linux_load(role)
    except (OSError, subprocess.TimeoutExpired):
        raise CredentialError("local Secret Service unavailable") from None
    if r.returncode:
        raise CredentialError("worker credential not available")
    return validate_token(r.stdout.rstrip("\r\n"))


def _windows_api():
    import ctypes
    from ctypes import wintypes

    class Credential(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]
    return ctypes, wintypes, Credential, ctypes.WinDLL("Advapi32.dll", use_last_error=True)


def _windows_save(role: str, token: str) -> None:
    try:
        ctypes, wintypes, Credential, api = _windows_api()
        write = api.CredWriteW
        write.argtypes = [ctypes.POINTER(Credential), wintypes.DWORD]
        write.restype = wintypes.BOOL
        blob = ctypes.create_string_buffer(token.encode("ascii"))
        item = Credential()
        item.Type = 1  # CRED_TYPE_GENERIC
        item.TargetName = "RezonTKIK/worker/" + role
        item.UserName = role
        item.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_ubyte))
        item.CredentialBlobSize = len(token)
        item.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE; current Windows user
        success = write(ctypes.byref(item), 0)
    except (OSError, AttributeError, TypeError, ValueError):
        raise CredentialError("Windows Credential Manager unavailable") from None
    if not success:
        raise CredentialError("Windows Credential Manager rejected enrollment")


def _windows_load(role: str) -> str:
    try:
        ctypes, wintypes, Credential, api = _windows_api()
        read = api.CredReadW
        read.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                         ctypes.POINTER(ctypes.POINTER(Credential))]
        read.restype = wintypes.BOOL
        free = api.CredFree
        free.argtypes = [ctypes.c_void_p]
        free.restype = None
        ptr = ctypes.POINTER(Credential)()
        if not read("RezonTKIK/worker/" + role, 1, 0, ctypes.byref(ptr)):
            raise CredentialError("no enrolled worker credential")
        try:
            size = ptr.contents.CredentialBlobSize
            if not 16 <= size <= 256:
                raise CredentialError("stored credential invalid")
            token = ctypes.string_at(ptr.contents.CredentialBlob, size).decode("ascii")
        finally:
            free(ctypes.cast(ptr, ctypes.c_void_p))
        return validate_token(token)
    except CredentialError:
        raise
    except (OSError, AttributeError, TypeError, ValueError, UnicodeError):
        raise CredentialError("Windows Credential Manager unavailable") from None


def save(role: str, token: str) -> None:
    validate_role(role)
    validate_token(token)
    if sys.platform == "win32":
        _windows_save(role, token)
    elif sys.platform.startswith("linux"):
        _linux_save(role, token)
    else:
        raise CredentialError("unsupported OS credential vault")


def load(role: str) -> str:
    validate_role(role)
    if sys.platform == "win32":
        return _windows_load(role)
    if sys.platform.startswith("linux"):
        return _linux_load(role)
    raise CredentialError("unsupported OS credential vault")
