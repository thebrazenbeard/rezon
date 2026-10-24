"""Local OS credential store (implementation pending TDD)."""
import subprocess
import sys

class CredentialError(ValueError):
    pass

def save(role: str, token: str) -> None:
    raise NotImplementedError("owner credential storage not implemented")

def load(role: str) -> str:
    raise NotImplementedError("owner credential storage not implemented")
