from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.sections import TableSection

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.blog.constants import POSTS_COUNT_DESCRIPTION, POSTS_SECTION_HEIGHT
from apps.blog.models import Category, Comment, Post, Tag


class PostsCountAdmin(ModelAdmin):

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
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "author", "status", "created_at")
    search_fields = ("title",)

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("body",)
