"""Console entry point for an installed SafeGloss Core distribution."""

import os
import sys


def main() -> None:
    """Run Django management commands with SafeGloss Core's settings module."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(["safegloss-core", *sys.argv[1:]])
