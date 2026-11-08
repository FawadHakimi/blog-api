from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter, RangeDateTimeFilter
from unfold.decorators import display
from unfold.sections import TableSection

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.text import Truncator

from apps.blog.constants import (
    COMMENT_BODY_PREVIEW_LENGTH,
    POSTS_COUNT_DESCRIPTION,
    POSTS_SECTION_HEIGHT,
)
from apps.blog.models import Category, Comment, Post, Tag


class PostsCountAdmin(ModelAdmin):
    """Shared admin for Category and Tag: auto slug, search and a sortable posts count."""

    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # One query counts the posts of every row (no .count() per row).
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description=POSTS_COUNT_DESCRIPTION, ordering="posts_count")
    def posts_count(self, obj: Category | Tag) -> int:
        return obj.posts_count


class CategoryPostsSection(TableSection):
    """Shown when a Category row is expanded: the posts of this category."""

    verbose_name = "Posts in this category"
    height = POSTS_SECTION_HEIGHT
    related_name = "posts"
    fields = ["title", "status", "created_at"]


@admin.register(Category)
class CategoryAdmin(PostsCountAdmin):
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # The expandable rows read category.posts, so load them in one extra query.
        return super().get_queryset(request).prefetch_related("posts")


@admin.register(Tag)
class TagAdmin(PostsCountAdmin):
    pass


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "author", "status", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("post_title", "author", "short_body", "created_at")
    list_filter = [
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ("body", "author__email", "post__title")
    autocomplete_fields = ("post", "author")
    # Load post and author in the same query as the comments (no N+1).
    list_select_related = ("post", "author")
    ordering = ("-created_at",)

    @display(description="Post", ordering="post__title")
    def post_title(self, obj: Comment) -> str:
        return obj.post.title

    @display(description="Body")
    def short_body(self, obj: Comment) -> str:
        return Truncator(obj.body).chars(COMMENT_BODY_PREVIEW_LENGTH)
