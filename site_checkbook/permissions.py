
from django.contrib.auth.models import Group


def is_hr_reviewer(user):
    if not user.is_authenticated:
        return False

    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["HR", "Supervisors"]
        ).exists()
    )


def can_manage_projects(user):
    if not user.is_authenticated:
        return False

    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["HR", "Supervisors", "Project Managers"]
        ).exists()
    )
