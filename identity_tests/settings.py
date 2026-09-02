import environ

SECRET_KEY = "unsafe-identity-contract-tests-only"
DEBUG = True
USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "safegloss_core_identity",
]
AUTH_USER_MODEL = "safegloss_core_identity.User"

env = environ.Env()
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgresql://localhost:5432/safegloss_identity_test",
    )
}
