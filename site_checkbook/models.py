# site_checkbook/models.py

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    project_code = models.CharField(max_length=50, unique=True)
    client = models.CharField(max_length=200, blank=True)
    site_location = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    engineers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="checkbook_projects",
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.project_code} - {self.name}"


class SiteActivity(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
        ("returned", "Returned for Correction"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="activities",
    )

    engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="site_activities",
    )

    activity_date = models.DateField()
    work_type = models.CharField(max_length=150)
    work_description = models.TextField()

    workers_count = models.PositiveIntegerField(default=0)

    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    materials_used = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    safety_observations = models.TextField(blank=True)
    next_day_plan = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.activity_date}"


class ActivityPhoto(models.Model):
    activity = models.ForeignKey(
        SiteActivity,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to="site_checkbook/activities/"
    )

    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for activity {self.activity_id}"