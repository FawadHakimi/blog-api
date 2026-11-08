from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse

from apps.blog.constants import (
    POST_CHANGELIST_URL_NAME,
    POST_STATUS_DRAFT,
    POST_STATUS_FILTER_PARAM,
    POST_STATUS_PUBLISHED,
)


def _post_list_link(status: str | None = None) -> str:
    url = reverse(POST_CHANGELIST_URL_NAME)
    if status is None:
        return url
    return f"{url}?{urlencode({POST_STATUS_FILTER_PARAM: status})}"


def posts_all_link(request: HttpRequest) -> str:
    return _post_list_link()


def posts_published_link(request: HttpRequest) -> str:
    return _post_list_link(POST_STATUS_PUBLISHED)


def posts_drafts_link(request: HttpRequest) -> str:
    return _post_list_link(POST_STATUS_DRAFT)
