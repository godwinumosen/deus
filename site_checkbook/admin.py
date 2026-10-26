
from django.contrib import admin

from .models import (
    ActivityPhoto,
    Checklist,
    ChecklistQuestion,
    ChecklistSubmission,
    ChecklistResponse,
    Department,
    Project,
    SiteActivity,
)


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
    readonly_fields = ("created_at", "updated_at")
    inlines = [ActivityPhotoInline]
    date_hierarchy = "activity_date"


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "caption", "uploaded_at")
    search_fields = (
        "caption",
        "activity__work_type",
        "activity__project__name",
    )
    readonly_fields = ("uploaded_at",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


class ChecklistQuestionInline(admin.TabularInline):
    model = ChecklistQuestion
    extra = 1
    fields = ("question_text", "is_required", "order")
    ordering = ("order",)


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "is_active", "created_at")
    list_filter = ("department", "is_active")
    search_fields = ("title", "department__name")
    inlines = [ChecklistQuestionInline]


@admin.register(ChecklistQuestion)
class ChecklistQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "checklist",
        "is_required",
        "order",
    )
    list_filter = ("is_required", "checklist__department")
    search_fields = ("question_text", "checklist__title")
    list_editable = ("is_required", "order")


class ChecklistResponseInline(admin.TabularInline):
    model = ChecklistResponse
    extra = 0
    fields = ("question", "answer", "comments")
    readonly_fields = ("question",)


@admin.register(ChecklistSubmission)
class ChecklistSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "checklist",
        "engineer",
        "project",
        "inspection_date",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "inspection_date",
        "checklist__department",
        "project",
    )
    search_fields = (
        "checklist__title",
        "engineer__username",
        "engineer__first_name",
        "engineer__last_name",
        "project__name",
    )
    readonly_fields = ("submitted_at", "reviewed_at")
    inlines = [ChecklistResponseInline]
    date_hierarchy = "inspection_date"


@admin.register(ChecklistResponse)
class ChecklistResponseAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "submission",
        "answer",
        "comments",
    )
    list_filter = ("answer", "submission__checklist__department")
    search_fields = (
        "question__question_text",
        "submission__engineer__username",
        "comments",
    )
