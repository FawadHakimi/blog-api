from typing import Any

from django.http import HttpRequest

from apps.blog.constants import (
    ENV_ID_PROD,
    ENV_LABEL_LOCAL,
    ENV_LABEL_PROD,
    ENV_TYPE_LOCAL,
    ENV_TYPE_PROD,
)
from apps.blog.models import Post
from settings import conf


def environment_callback(request: HttpRequest) -> list[str]:
    if conf.ENV_ID == ENV_ID_PROD:
        return [ENV_LABEL_PROD, ENV_TYPE_PROD]
    return [ENV_LABEL_LOCAL, ENV_TYPE_LOCAL]

def drafts_badge(request: HttpRequest) -> str:
    return str(Post.objects.filter(status=Post.Status.DRAFT).count())

def superuser_only(request: HttpRequest) -> bool:
    return request.user.is_superuser

def dashboard_callback(requset: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    return context
