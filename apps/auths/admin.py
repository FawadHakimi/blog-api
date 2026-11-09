from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.auths.forms import UserAdminChangeForm, UserAdminCreationForm
from apps.auths.models import User
from apps.blog.constants import (
    LABEL_DANGER,
    LABEL_INFO,
    LABEL_NEUTRAL,
    LABEL_SUCCESS,
    USER_ACTIVE_TEXT,
    USER_INACTIVE_TEXT,
    USER_REGULAR_TEXT,
    USER_STAFF_TEXT,
    USERS_ACTIVATED_MESSAGE,
    USERS_DEACTIVATED_MESSAGE,
)

# Django registers Group with the plain admin. Re-register it with Unfold.
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    change_password_form = AdminPasswordChangeForm

    ordering = ("email",)
    list_display = ("user_header", "active_label", "staff_label", "posts_count")
    list_filter = [
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter),
    ]
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("last_login",)
    filter_horizontal = ("groups", "user_permissions")
    actions = ["activate_users", "deactivate_users"]

    # The edit form is split into tabs.
    fieldsets = (
        (
            "Personal info",
            {
                "classes": ["tab"],
                "fields": ("email", "password", "first_name", "last_name"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ["tab"],
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"classes": ["tab"], "fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ["wide"],
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description="User", header=True, ordering="email")
    def user_header(self, obj: User) -> list[str]:
        full_name = f"{obj.first_name} {obj.last_name}"
        initials = f"{obj.first_name[:1]}{obj.last_name[:1]}".upper()
        return [full_name, obj.email, initials]

    @display(
        description="Active",
        ordering="is_active",
        label={True: LABEL_SUCCESS, False: LABEL_DANGER},
    )
    def active_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_active, USER_ACTIVE_TEXT if obj.is_active else USER_INACTIVE_TEXT

    @display(
        description="Staff",
        ordering="is_staff",
        label={True: LABEL_INFO, False: LABEL_NEUTRAL},
    )
    def staff_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_staff, USER_STAFF_TEXT if obj.is_staff else USER_REGULAR_TEXT

    @display(description="Posts", ordering="posts_count")
    def posts_count(self, obj: User) -> int:
        return obj.posts_count

    @action(description="Activate selected users", permissions=["change"])
    def activate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        ids = list(queryset.values_list("pk", flat=True))
        updated = User.objects.filter(pk__in=ids).update(is_active=True)
        self.message_user(request, USERS_ACTIVATED_MESSAGE.format(count=updated))

    @action(description="Deactivate selected users", permissions=["change"])
    def deactivate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        # Never let an admin lock themselves out.
        ids = list(queryset.exclude(pk=request.user.pk).values_list("pk", flat=True))
        updated = User.objects.filter(pk__in=ids).update(is_active=False)
        self.message_user(request, USERS_DEACTIVATED_MESSAGE.format(count=updated))
