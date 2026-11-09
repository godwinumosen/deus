from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


def send_submission_notification(submission, request):
    """Notify HR and Supervisors when an engineer submits a checklist."""

    recipients = list(
        User.objects.filter(
            is_active=True
        ).filter(
            Q(groups__name__in=["HR", "Supervisors"])
            | Q(is_superuser=True)
        ).exclude(
            email__isnull=True
        ).exclude(
            email=""
        ).values_list(
            "email", flat=True
        ).distinct()
    )

    if not recipients:
        logger.warning(
            "No HR or Supervisor email recipients found."
        )
        return

    review_url = request.build_absolute_uri(
        reverse(
            "site_checkbook:checklist_review_detail",
            args=[submission.pk]
        )
    )

    try:
        send_mail(
            subject="New Site Checklist Submitted - Awaiting Review",
            message=f"""
A new site checklist has been submitted and is awaiting review.

Engineer: {submission.engineer.get_full_name() or submission.engineer.username}
Engineer Email: {submission.engineer.email}

Project: {submission.project.name}
Checklist: {submission.checklist.title}
Department: {submission.checklist.department.name}
Inspection Date: {submission.inspection_date}

Please log in to the Site Checkbook system to review this submission.

Review Checklist:
{review_url}

Deus Magnus Site Checkbook
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        logger.info(
            "Checklist notification sent for submission %s to %s",
            submission.pk,
            recipients,
        )

    except Exception:
        logger.exception(
            "Failed to send checklist notification for submission %s",
            submission.pk,
        )