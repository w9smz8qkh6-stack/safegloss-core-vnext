import uuid
from importlib import import_module
from pathlib import Path

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, connection


@pytest.mark.django_db
def test_identity_root_model_contract():
    user_model = get_user_model()

    assert user_model._meta.label == "safegloss_core_identity.User"
    assert user_model._meta.db_table == "safegloss_core_identity_user"
    assert user_model.USERNAME_FIELD == "email"
    assert user_model.REQUIRED_FIELDS == []
    assert user_model._meta.get_field("id").get_internal_type() == "UUIDField"
    assert user_model._meta.get_field("email").unique is True
    assert {field.name for field in user_model._meta.fields}.isdisjoint(
        {"username", "first_name", "last_name"}
    )
    assert user_model._meta.get_field("groups").remote_field.through._meta.db_table == (
        "safegloss_core_identity_user_groups"
    )
    assert user_model._meta.get_field("user_permissions").remote_field.through._meta.db_table == (
        "safegloss_core_identity_user_permissions"
    )


@pytest.mark.django_db
def test_manager_normalizes_email_and_hashes_password():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        "  teacher@EXAMPLE.COM  ", password="not-plaintext", display_name="Teacher"
    )

    assert isinstance(user.pk, uuid.UUID)
    assert user.email == "teacher@example.com"
    assert user.password != "not-plaintext"
    assert user.check_password("not-plaintext")
    assert user.get_full_name() == "Teacher"
    assert user.get_short_name() == "Teacher"


@pytest.mark.django_db
def test_manager_rejects_missing_email_and_invalid_superuser_flags():
    user_model = get_user_model()

    with pytest.raises(ValueError, match="email"):
        user_model.objects.create_user("")
    with pytest.raises(ValueError, match="is_staff"):
        user_model.objects.create_superuser("admin@example.com", "password", is_staff=False)
    with pytest.raises(ValueError, match="is_superuser"):
        user_model.objects.create_superuser("admin@example.com", "password", is_superuser=False)


@pytest.mark.django_db(transaction=True)
def test_duplicate_canonical_email_is_refused_by_postgresql():
    user_model = get_user_model()
    user_model.objects.create_user("member@example.com", "password")

    with pytest.raises(IntegrityError):
        user_model.objects.create_user("member@example.com", "different-password")


@pytest.mark.django_db
def test_inactive_user_cannot_authenticate():
    user_model = get_user_model()
    user_model.objects.create_user("inactive@example.com", "password", is_active=False)

    assert authenticate(username="inactive@example.com", password="password") is None


@pytest.mark.django_db
def test_user_creation_has_no_email_or_network_side_effect(monkeypatch):
    def fail_on_call(*args, **kwargs):
        raise AssertionError("identity creation attempted external I/O")

    monkeypatch.setattr("socket.socket.connect", fail_on_call)
    monkeypatch.setattr("django.core.mail.send_mail", fail_on_call)

    user = get_user_model().objects.create_user("local@example.com", "password")
    assert user.email == "local@example.com"


def test_first_migration_has_only_the_django_auth_dependency():
    migration = import_module("safegloss_core_identity.migrations.0001_user").Migration

    assert migration.initial is True
    assert migration.dependencies == [("auth", "0012_alter_user_first_name_max_length")]


def test_sibling_apps_do_not_import_the_staged_concrete_user():
    repository = Path(__file__).resolve().parents[1]
    sibling_apps = ("accounts", "core", "courses", "glossary", "config")

    offenders = []
    for app in sibling_apps:
        for source in (repository / app).rglob("*.py"):
            if "safegloss_core_identity" in source.read_text(encoding="utf-8"):
                offenders.append(source.relative_to(repository).as_posix())
    assert offenders == []


@pytest.mark.django_db
def test_postgresql_schema_contract():
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
        constraints = connection.introspection.get_constraints(
            cursor, "safegloss_core_identity_user"
        )

    identity_tables = {name for name in tables if name.startswith("safegloss_core_identity_")}
    assert identity_tables == {
        "safegloss_core_identity_user",
        "safegloss_core_identity_user_groups",
        "safegloss_core_identity_user_permissions",
    }
    assert constraints["sgc_user_email_uq"]["unique"] is True
    assert "safegloss_core_identity_user_email_key" not in constraints
