from django.contrib import admin

from .models import DBFile


@admin.register(DBFile)
class DBFileAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("name",)
    readonly_fields = ("name", "content_type", "size", "created_at")

    def has_add_permission(self, request):
        return False
