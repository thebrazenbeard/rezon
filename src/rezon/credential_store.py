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


def _linux_save(role: str, token: str) -> None:
    try:
        r = subprocess.run(
            ["secret-tool", "store", "--label=Rezon worker " + role,
             "service", "rezon-tkik", "role", role],
            input=token + "\n", capture_output=True, text=True, timeout=25,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        raise CredentialError("local Secret Service unavailable") from None
    if r.returncode:
        raise CredentialError("local Secret Service could not store credential")


def _linux_load(role: str) -> str:
    try:
        r = subprocess.run(
            ["secret-tool", "lookup", "service", "rezon-tkik", "role", role],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
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
