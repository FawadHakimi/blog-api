from unfold.admin import ModelAdmin

from django.contrib import admin
from django.contrib.auth.models import Group

from apps.auths.models import User

# Django registers Group with the plain admin. Re-register it with Unfold.
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
