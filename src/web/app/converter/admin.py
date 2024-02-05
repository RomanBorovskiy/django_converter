from django.contrib import admin
from django.db.utils import OperationalError, ProgrammingError

from .models import Doc, Settings


class DocAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_at", "status")
    list_display_links = ("id", "title")
    search_fields = ("title",)


admin.site.register(Doc, DocAdmin)


# Register your models here.


class SettingsAdmin(admin.ModelAdmin):
    # Create a default object on the first page of SiteSettingsAdmin with a list of settings
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # be sure to wrap the loading and saving Settings in a try catch,
        # so that you can create database migrations
        try:
            Settings.load().save()
        except (ProgrammingError, OperationalError):
            pass

    # prohibit adding new settings
    def has_add_permission(self, request, obj=None):
        return False

    # as well as deleting existing
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)
