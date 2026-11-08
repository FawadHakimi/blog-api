from unfold.admin import ModelAdmin

from django.contrib import admin

from apps.blog.models import Category, Comment, Post, Tag


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
