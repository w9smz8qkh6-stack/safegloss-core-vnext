"""Minimal settings used only to verify installed identity-root artifacts."""

import environ

SECRET_KEY = "unsafe-artifact-smoke-only"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "safegloss_core_identity",
]
AUTH_USER_MODEL = "safegloss_core_identity.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {"default": environ.Env().db("DATABASE_URL")}
