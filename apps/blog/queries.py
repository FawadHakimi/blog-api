from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

from django.db.models import F, Q, QuerySet, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.auths.models import User
from apps.blog.constants import (
    EDITED_AFTER_HOURS,
    EMAIL_DOMAIN_PREFIX,
    NEWEST_POSTS_LIMIT,
    POSTS_PER_PAGE,
    UNCATEGORIZED_LABEL,
)
from apps.blog.models import Category, Comment, Post

# ---------------------------------------------------------------- Level 1


def categories_by_name() -> QuerySet[Category]:
    """Return all categories sorted by name A to Z."""
    return Category.objects.order_by("name")


def published_posts() -> QuerySet[Post]:
    """Return published posts, newest first."""
    return Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")


def newest_published_posts() -> QuerySet[Post]:
    """Return the newest published posts (the limit is NEWEST_POSTS_LIMIT)."""
    return published_posts()[:NEWEST_POSTS_LIMIT]


def post_by_slug(slug: str) -> Post | None:
    """Return the post with this slug, or None if there is no such post."""
    return Post.objects.filter(slug=slug).first()


def active_users_count() -> int:
    """Return the number of active users. Staff users are not counted."""
    return User.objects.filter(is_active=True, is_staff=False).count()


def has_drafts() -> bool:
    """Return True if there is at least one draft post."""
    return Post.objects.filter(status=Post.Status.DRAFT).exists()


def published_posts_page(page: int) -> QuerySet[Post]:
    """Return one page of published posts, newest first. Page 1 is the first page."""
    page = max(page, 1)  # a page number below 1 would make a negative slice
    start = (page - 1) * POSTS_PER_PAGE
    return published_posts()[start : start + POSTS_PER_PAGE]


# ---------------------------------------------------------------- Level 2


def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """Return posts whose title contains the word (letter case does not matter)."""
    return Post.objects.filter(title__icontains=word)


def users_with_email_domain(domain: str) -> QuerySet[User]:
    """Return users whose email ends with @ + domain (letter case does not matter)."""
    return User.objects.filter(email__iendswith=f"{EMAIL_DOMAIN_PREFIX}{domain}")


def posts_without_category() -> QuerySet[Post]:
    """Return posts that have no category."""
    return Post.objects.filter(category__isnull=True)


def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    """Return categories whose slug is in the given list."""
    return Category.objects.filter(slug__in=slugs)


def posts_in_month(year: int, month: int) -> QuerySet[Post]:
    """Return posts created in this month of this year."""
    return Post.objects.filter(created_at__year=year, created_at__month=month)


def posts_last_days(days: int) -> QuerySet[Post]:
    """Return posts created in the last `days` days."""
    since = timezone.now() - timedelta(days=days)
    return Post.objects.filter(created_at__gte=since)


def posts_between(start: date, end: date) -> QuerySet[Post]:
    """Return posts created from the start day to the end day (both days included)."""
    return Post.objects.filter(created_at__date__range=(start, end))


# ---------------------------------------------------------------- Level 3


def author_published_posts(email: str) -> QuerySet[Post]:
    """Return published posts of the author with this email (letter case does not matter)."""
    return Post.objects.filter(status=Post.Status.PUBLISHED, author__email__iexact=email)


def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """Return posts that have the tag with this slug."""
    return Post.objects.filter(tags__slug=tag_slug)


def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """Return comments on posts of the category with this slug."""
    return Comment.objects.filter(post__category__slug=category_slug)


def users_with_published_posts() -> QuerySet[User]:
    """Return users who have at least one published post. Every user appears once."""
    return User.objects.filter(posts__status=Post.Status.PUBLISHED).distinct()


def posts_without_tags() -> QuerySet[Post]:
    """Return posts that have no tags."""
    return Post.objects.filter(tags__isnull=True)


def users_without_comments() -> QuerySet[User]:
    """Return users who have never written a comment."""
    return User.objects.filter(comments__isnull=True)


def posts_with_both_tags(first_slug: str, second_slug: str) -> QuerySet[Post]:
    """Return posts that have both tags. Two filter() calls make two separate joins."""
    return Post.objects.filter(tags__slug=first_slug).filter(tags__slug=second_slug)


# ---------------------------------------------------------------- Level 4


def search_posts(text: str) -> QuerySet[Post]:
    """Return posts that have the text in the title or in the body (case-insensitive)."""
    return Post.objects.filter(Q(title__icontains=text) | Q(body__icontains=text))


def published_posts_missing_info() -> QuerySet[Post]:
    """Return published posts with no category or no tags. Every post appears once."""
    return Post.objects.filter(
        Q(category__isnull=True) | Q(tags__isnull=True),
        status=Post.Status.PUBLISHED,
    ).distinct()


def edited_posts() -> QuerySet[Post]:
    """Return posts edited more than EDITED_AFTER_HOURS hours after they were created."""
    threshold = timedelta(hours=EDITED_AFTER_HOURS)
    return Post.objects.filter(updated_at__gt=F("created_at") + threshold)


def comments_by_post_author() -> QuerySet[Comment]:
    """Return comments that the author of the post wrote under their own post."""
    return Comment.objects.filter(author=F("post__author"))


def comments_before_post() -> QuerySet[Comment]:
    """Return comments created before their post. Must be empty if the seed dates are right."""
    return Comment.objects.filter(created_at__lt=F("post__created_at"))


# ---------------------------------------------------------------- Level 5


def published_authors_emails() -> list[str]:
    """Return unique emails of authors who have published posts, sorted A to Z."""
    emails = (
        User.objects.filter(posts__status=Post.Status.PUBLISHED)
        .values_list("email", flat=True)
        .distinct()
        .order_by("email")
    )
    return list(emails)


def published_posts_overview() -> list[dict[str, Any]]:
    """Return title, author_email and category_name of every published post."""
    rows = (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .order_by("-created_at")
        .values(
            "title",
            author_email=F("author__email"),
            category_name=Coalesce("category__name", Value(UNCATEGORIZED_LABEL)),
        )
    )
    return list(rows)


QUERIES: dict[int, Callable[..., Any]] = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_month,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_posts_overview,
}
