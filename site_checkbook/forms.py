# site_checkbook/forms.py

from django import forms

from .models import Project, SiteActivity
from .permissions import is_hr_reviewer


class SiteActivityForm(forms.ModelForm):

    class Meta:
        model = SiteActivity

        fields = [
            "project",
            "activity_date",
            "work_type",
            "work_description",
            "workers_count",
            "progress_percentage",
            "materials_used",
            "challenges",
            "safety_observations",
            "next_day_plan",
        ]

        widgets = {
            "project": forms.Select(
                attrs={"class": "form-select"}
            ),
            "activity_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "work_type": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "work_description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": (
                        "Describe the actual work completed today, "
                        "e.g. Foundation excavation completed for Block A."
                    ),
                    "required": True,
                }
            ),
            "workers_count": forms.NumberInput(
                attrs={
                    "min": 0,
                    "class": "form-control",
                }
            ),
            "progress_percentage": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 100,
                    "class": "form-control",
                }
            ),
            "materials_used": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                }
            ),
            "challenges": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                }
            ),
            "safety_observations": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                }
            ),
            "next_day_plan": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        projects = Project.objects.filter(is_active=True)

        if user is not None and not is_hr_reviewer(user):
            projects = projects.filter(
                engineers__id=user.pk
            )

        self.fields["project"].queryset = projects.distinct()
        self.fields["project"].empty_label = "Select your project"

from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectForm(forms.ModelForm):
    engineers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            is_superuser=False,
        ).exclude(
            groups__name__in=["HR", "Supervisors"]
        ).distinct(),
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "size": "5",
            }
        ),
        required=False,
        help_text="Select the engineers assigned to this project.",
    )

    class Meta:
        model = Project
        fields = [
            "name",
            "project_code",
            "client",
            "site_location",
            "description",
            "engineers",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "project_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "client": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "site_location": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }