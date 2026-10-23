# site_checkbook/admin.py

from django.contrib import admin

from .models import ActivityPhoto, Project, SiteActivity


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code",
        "name",
        "client",
        "site_location",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)

    search_fields = (
        "project_code",
        "name",
        "client",
        "site_location",
    )

    filter_horizontal = ("engineers",)


class ActivityPhotoInline(admin.TabularInline):
    model = ActivityPhoto
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(SiteActivity)
class SiteActivityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "engineer",
        "activity_date",
        "work_type",
        "progress_percentage",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "activity_date",
        "project",
        "work_type",
    )

    search_fields = (
        "project__name",
        "project__project_code",
        "engineer__username",
        "engineer__first_name",
        "engineer__last_name",
        "work_type",
        "work_description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [ActivityPhotoInline]
    date_hierarchy = "activity_date"


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "activity",
        "caption",
        "uploaded_at",
    )

    search_fields = (
        "caption",
        "activity__work_type",
        "activity__project__name",
    )

    readonly_fields = ("uploaded_at",)