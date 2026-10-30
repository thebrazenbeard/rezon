"""Fail-closed v2 protected-structure candidate admission."""

class AdmissionGateError(ValueError):
    pass


def scan_v2_manifest(*args):
    raise AdmissionGateError("not implemented")


def filter_protected(*args, **kwargs):
    raise AdmissionGateError("not implemented")


def verify_wave(*args):
    raise AdmissionGateError("not implemented")
