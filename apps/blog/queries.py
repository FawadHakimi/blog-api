from collections.abc import Callable
from typing import Any

from django.db.models import QuerySet

from apps.auths.models import User
from apps.blog.constants import NEWEST_POSTS_LIMIT, POSTS_PER_PAGE
from apps.blog.models import Category, Post

# ----------------------------------------------------------------------- Level 1

def categories_by_name() -> QuerySet[Category]:
    return Category.objects.order_by("name")


def published_posts() -> QuerySet[Post]:
    return Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")


def newest_published_posts() -> QuerySet[Post]:
    return published_posts()[:NEWEST_POSTS_LIMIT]


def post_by_slug(slug: str) -> Post | None:
    return Post.objects.filter(slug=slug).first()


def active_users_count() -> int:
    return User.objects.filter(is_active=True, is_staff=False).count()


def has_drafts() -> bool:
    return Post.objects.filter(status=Post.Status.DRAFT).exists()


def published_posts_page(page: int) -> QuerySet[Post]:
    page = max(page, 1)
    start = (page - 1) * POSTS_PER_PAGE
    return published_posts()[start: start + POSTS_PER_PAGE]



QUERIES: dict[int, Callable[..., Any]] = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
}
