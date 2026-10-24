"""Role-bound operator-local enrollment (implementation pending TDD)."""
import getpass
import sys

from . import credential_store
from .worker_client import run as client_run

class EnrollmentError(ValueError):
    pass

def enroll(role: str, gateway: str, episode: str) -> dict:
    raise NotImplementedError("owner enrollment not implemented")

def execute(action: str, role: str, gateway: str, episode: str,
            model_id: str | None = None, model_url: str = "http://127.0.0.1:11434/v1",
            model_key: str | None = None, timeout: int = 120,
            max_tokens: int = 240) -> dict:
    raise NotImplementedError("enrolled execution not implemented")

def main(argv=None) -> int:
    raise NotImplementedError("local owner CLI not implemented")
