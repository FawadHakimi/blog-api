from collections.abc import Callable
from typing import Any

from django.db.models import QuerySet

from apps.blog.models import Category, Post


def categories_by_name() -> QuerySet[Category]:
    return Category.objects.order_by("name")


def has_drafts() -> bool:
    return Post.objects.filter(status=Post.Status.DRAFT).exists()


QUERIES: dict[int, Callable[..., Any]] = {
    1: categories_by_name,
    6: has_drafts,
}
