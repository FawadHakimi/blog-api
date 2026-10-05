from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager

from apps.auths.constants import (
    EMAIL_REQUIRED_ERROR,
    SUPERUSER_FLAG_ERROR,
    SUPERUSER_STAFF_ERROR,
)

if TYPE_CHECKING:
    from apps.auths.models import User


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        if not email:
            raise ValueError(EMAIL_REQUIRED_ERROR)
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(SUPERUSER_STAFF_ERROR)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(SUPERUSER_FLAG_ERROR)
        return self.create_user(email, password, **extra_fields)