from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.sections import TableSection

from django.contrib import admin
from django.db import models
from django.db.models import Count, Prefetch, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.text import Truncator
from django.utils.translation import ngettext

from apps.blog.constants import (
    COMMENT_BODY_PREVIEW_LENGTH,
    COMMENT_LIST_URL_NAME,
    COMMENT_POST_FILTER_PARAM,
    COMMENTS_INLINE_PER_PAGE,
    LABEL_SUCCESS,
    LABEL_WARNING,
    POST_CHANGELIST_URL_NAME,
    POST_PUBLISHED_MESSAGE,
    POST_UNPUBLISHED_MESSAGE,
    POSTS_COMMENT_SECTION_TITLE,
    POSTS_COUNT_DESCRIPTION,
    POSTS_MOVED_TO_DRAFTS_MESSAGE,
    POSTS_PUBLISHED_MESSAGE,
    POSTS_SECTION_HEIGHT,
    TAGS_DROPDOWN_HEIGHT,
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


class PostCommentsSection(TableSection):
    """Shown when a Post row is expanded: the comments of this post."""

    verbose_name = POSTS_COMMENT_SECTION_TITLE
    height = POSTS_SECTION_HEIGHT
    related_name = "comments"
    fields = ["author", "short_body", "created_at"]

    @admin.display(description="Body")
    def short_body(self, instance: Comment) -> str:
        return Truncator(instance.body).chars(COMMENT_BODY_PREVIEW_LENGTH)


class CommentInline(TabularInline):
    """Comments inside the post edit page: own tab, 10 per page."""

    model = Comment
    tab = True
    per_page = COMMENTS_INLINE_PER_PAGE
    extra = 0
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)
    ordering = ("-created_at",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "post_header",
        "status_label",
        "category",
        "tags_dropdown",
        "comments_count",
        "created_at",
    )
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ("title", "body", "author__email")
    list_select_related = ("author", "category")
    list_sections = [PostCommentsSection]
    ordering = ("-created_at",)

    # Edit page
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category", "tags")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CommentInline]
    warn_unsaved_form = True
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    fieldsets = (
        ("Content", {"classes": ["tab"], "fields": ("title", "slug", "body")}),
        (
            "Classification",
            {"classes": ["tab"], "fields": ("category", "tags", "status")},
        ),
        ("Meta", {"classes": ["tab"], "fields": ("author", "created_at", "updated_at")}),
    )

    # Actions
    actions = ["publish_selected", "move_to_drafts"]  # bulk, with checkboxes
    actions_row = ["toggle_publish"]  # in every row
    actions_list = ["publish_all_drafts"]  # above the list
    actions_detail = ["open_comments"]  # on the post page
    actions_submit_line = ["save_and_publish"]  # next to the Save button

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        comments = Comment.objects.select_related("author").order_by("-created_at")
        return (
            super()
            .get_queryset(request)
            .annotate(comments_count=Count("comments", distinct=True))
            .prefetch_related("tags", Prefetch("comments", queryset=comments))
        )

    # ----- columns -----

    @display(description="Post", header=True, ordering="title")
    def post_header(self, obj: Post) -> list[str]:
        author = f"{obj.author.first_name} {obj.author.last_name}"
        initials = f"{obj.author.first_name[:1]}{obj.author.last_name[:1]}".upper()
        return [obj.title, author, initials]

    @display(
        description="Status",
        ordering="status",
        label={Post.Status.PUBLISHED: LABEL_SUCCESS, Post.Status.DRAFT: LABEL_WARNING},
    )
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description="Tags", dropdown=True)
    def tags_dropdown(self, obj: Post) -> dict:
        # len(...all()) uses the prefetched tags; .count() would query every row.
        tags = obj.tags.all()
        total = len(tags)
        return {
            "title": ngettext("%(count)d tag", "%(count)d tags", total) % {"count": total},
            "height": TAGS_DROPDOWN_HEIGHT,
            "items": [{"title": tag.name} for tag in tags],
        }

    @display(description="Comments", ordering="comments_count")
    def comments_count(self, obj: Post) -> int:
        return obj.comments_count

    # ----- helpers -----

    def _set_status(self, queryset: QuerySet[Post], status: str) -> int:
        ids = list(queryset.values_list("pk", flat=True))
        return Post.objects.filter(pk__in=ids).update(
            status=status, updated_at=timezone.now()
        )

    def _back_to_list(self, request: HttpRequest) -> HttpResponse:
        """Go back to the page we came from (keeps filters), or to the post list."""
        referer = request.headers.get("referer", "")
        if referer and url_has_allowed_host_and_scheme(
            referer, allowed_hosts={request.get_host()}
        ):
            return redirect(referer)
        return redirect(reverse(POST_CHANGELIST_URL_NAME))

    # ----- bulk actions -----

    @action(description="Publish selected", permissions=["change"])
    def publish_selected(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        updated = self._set_status(queryset, Post.Status.PUBLISHED)
        self.message_user(request, POSTS_PUBLISHED_MESSAGE.format(count=updated))

    @action(description="Move to drafts", permissions=["change"])
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        updated = self._set_status(queryset, Post.Status.DRAFT)
        self.message_user(request, POSTS_MOVED_TO_DRAFTS_MESSAGE.format(count=updated))

    # ----- row action -----

    @action(description="Publish / unpublish", icon="swap_horiz", permissions=["change"])
    def toggle_publish(self, request: HttpRequest, object_id: int) -> HttpResponse:
        post = get_object_or_404(Post, pk=object_id)
        if post.status == Post.Status.PUBLISHED:
            post.status = Post.Status.DRAFT
            message = POST_UNPUBLISHED_MESSAGE
        else:
            post.status = Post.Status.PUBLISHED
            message = POST_PUBLISHED_MESSAGE
        post.save(update_fields=["status", "updated_at"])
        self.message_user(request, message.format(title=post.title))
        return self._back_to_list(request)

    # ----- action above the list -----

    @action(description="Publish all drafts", icon="publish", permissions=["change"])
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponse:
        drafts = Post.objects.filter(status=Post.Status.DRAFT)
        updated = self._set_status(drafts, Post.Status.PUBLISHED)
        self.message_user(request, POSTS_PUBLISHED_MESSAGE.format(count=updated))
        return self._back_to_list(request)

    # ----- action on the post page -----

    @action(description="Open comments", icon="forum")
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponse:
        query = urlencode({COMMENT_POST_FILTER_PARAM: object_id})
        return redirect(f"{reverse(COMMENT_LIST_URL_NAME)}?{query}")

    # ----- button next to Save (runs after the post is saved) -----

    @action(description="Save & publish", permissions=["change"])
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save(update_fields=["status", "updated_at"])
        self.message_user(request, POST_PUBLISHED_MESSAGE.format(title=obj.title))


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
