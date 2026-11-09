import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpRequest
from django.urls import reverse

from apps.blog.constants import (
    COMMENT_LIST_URL_NAME,
    DASHBOARD_CHART_COLOR,
    DASHBOARD_CHART_HEIGHT,
    DASHBOARD_TOP_AUTHORS_LIMIT,
    ENV_ID_PROD,
    ENV_LABEL_LOCAL,
    ENV_LABEL_PROD,
    ENV_TYPE_LOCAL,
    ENV_TYPE_PROD,
    PERCENT_DECIMALS,
    PERCENT_TOTAL,
    POST_CHANGELIST_URL_NAME,
    USER_LIST_URL_NAME,
)
from apps.blog.models import Category, Comment, Post
from settings import conf


def environment_callback(request: HttpRequest) -> list[str]:
    """Badge in the header: Local (orange) or Production (red)."""
    if conf.ENV_ID == ENV_ID_PROD:
        return [ENV_LABEL_PROD, ENV_TYPE_PROD]
    return [ENV_LABEL_LOCAL, ENV_TYPE_LOCAL]


def drafts_badge(request: HttpRequest) -> str:
    """Number of drafts, shown as a badge next to "Posts" in the sidebar."""
    return str(Post.objects.filter(status=Post.Status.DRAFT).count())


def superuser_only(request: HttpRequest) -> bool:
    """Permission callback: the menu item is visible only to superusers."""
    return request.user.is_superuser


def _percent(part: int, total: int) -> float:
    """Share of `part` in `total` as a percentage (0 when there is nothing to divide)."""
    if total == 0:
        return 0.0
    return round(part * PERCENT_TOTAL / total, PERCENT_DECIMALS)


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    """Adds the numbers for the admin home page. Everything is counted in the database."""
    user_model = get_user_model()

    # Cards. One query counts published posts and drafts together.
    post_totals = Post.objects.aggregate(
        published=Count("pk", filter=Q(status=Post.Status.PUBLISHED)),
        drafts=Count("pk", filter=Q(status=Post.Status.DRAFT)),
    )
    published: int = post_totals["published"]
    drafts: int = post_totals["drafts"]
    kpi_cards = [
        {
            "title": "Total users",
            "value": user_model.objects.count(),
            "icon": "group",
            "link": reverse(USER_LIST_URL_NAME),
        },
        {
            "title": "Published posts",
            "value": published,
            "icon": "article",
            "link": reverse(POST_CHANGELIST_URL_NAME),
        },
        {
            "title": "Drafts",
            "value": drafts,
            "icon": "edit_note",
            "link": reverse(POST_CHANGELIST_URL_NAME),
        },
        {
            "title": "Comments",
            "value": Comment.objects.count(),
            "icon": "forum",
            "link": reverse(COMMENT_LIST_URL_NAME),
        },
    ]

    # Bar chart: posts per category (Chart.js format, as a JSON string).
    categories = Category.objects.annotate(posts_count=Count("posts")).order_by("-posts_count")
    category_chart = json.dumps(
        {
            "labels": [category.name for category in categories],
            "datasets": [
                {
                    "label": "Posts",
                    "data": [category.posts_count for category in categories],
                    "backgroundColor": DASHBOARD_CHART_COLOR,
                }
            ],
        }
    )

    # Table: top authors by number of posts.
    top_authors = (
        user_model.objects.annotate(posts_count=Count("posts"))
        .filter(posts_count__gt=0)
        .order_by("-posts_count", "email")[:DASHBOARD_TOP_AUTHORS_LIMIT]
    )
    top_authors_table = {
        "headers": ["Author", "Email", "Posts"],
        "rows": [
            [f"{author.first_name} {author.last_name}", author.email, author.posts_count]
            for author in top_authors
        ],
    }

    # Progress bars: share of published and draft posts.
    total_posts = published + drafts
    progress_bars = [
        {
            "title": "Published",
            "value": _percent(published, total_posts),
            "description": f"{published} of {total_posts}",
        },
        {
            "title": "Drafts",
            "value": _percent(drafts, total_posts),
            "description": f"{drafts} of {total_posts}",
        },
    ]

    context.update(
        {
            "kpi_cards": kpi_cards,
            "category_chart": category_chart,
            "category_chart_height": DASHBOARD_CHART_HEIGHT,
            "top_authors_table": top_authors_table,
            "progress_bars": progress_bars,
        }
    )
    return context
