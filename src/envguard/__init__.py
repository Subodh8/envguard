"""
envguard — validate, audit, and generate .env files.

Usage:
    envguard check   → find missing or undocumented keys
    envguard audit   → detect potential secret leaks
    envguard generate → create .env.example from .env
    envguard diff    → compare two env files
"""

__version__ = "0.1.0"
__author__ = "EnvGuard Contributors"

from envguard.checker import check_env
from envguard.auditor import audit_env
from envguard.generator import generate_example

__all__ = ["check_env", "audit_env", "generate_example"]