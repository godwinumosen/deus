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




def send_activity_notification(activity, request):
    """Notify HR and Supervisors when an engineer submits a site report."""

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
            "No HR or Supervisor email recipients found for activity report."
        )
        return

    report_url = request.build_absolute_uri(
        reverse(
            "site_checkbook:activity_detail",
            args=[activity.pk]
        )
    )

    try:
        send_mail(
            subject="New Site Activity Report Submitted - Awaiting Review",
            message=f"""
A new site activity report has been submitted and is awaiting review.

Engineer: {activity.engineer.get_full_name() or activity.engineer.username}
Engineer Email: {activity.engineer.email}

Project: {activity.project.name}
Project Code: {activity.project.project_code}
Activity Date: {activity.activity_date}
Work Type: {activity.work_type}
Progress: {activity.progress_percentage}%

Work Description:
{activity.work_description}

Workers Count: {activity.workers_count}

Please log in to the Site Checkbook system to review this report.

View Report:
{report_url}

Deus Magnus Site Checkbook
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        logger.info(
            "Activity report notification sent for activity %s to %s",
            activity.pk,
            recipients,
        )

    except Exception:
        logger.exception(
            "Failed to send activity report notification for activity %s",
            activity.pk,
        )



def send_activity_review_notification(activity):
    """Notify engineer when HR reviews their site activity report."""

    engineer_email = activity.engineer.email

    if not engineer_email:
        logger.warning(
            "No email address found for engineer on activity %s",
            activity.pk,
        )
        return False

    if activity.status == "reviewed":
        subject = "Your Site Activity Report Has Been Reviewed"

        message = f"""
Hello {activity.engineer.get_full_name() or activity.engineer.username},

Your site activity report has been reviewed successfully by HR.

Project: {activity.project.name}
Activity Date: {activity.activity_date}
Work Type: {activity.work_type}

Status: REVIEWED

Thank you.

Deus Magnus Site Checkbook
"""

    elif activity.status == "returned":
        subject = "Your Site Activity Report Has Been Returned"

        message = f"""
Hello {activity.engineer.get_full_name() or activity.engineer.username},

Your site activity report has been returned for correction by HR.

Project: {activity.project.name}
Activity Date: {activity.activity_date}
Work Type: {activity.work_type}

Status: RETURNED FOR CORRECTION

Please log in to your Site Checkbook account, correct your report
and resubmit it.

Thank you.

Deus Magnus Site Checkbook
"""

    else:
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[engineer_email],
            fail_silently=False,
        )

        logger.info(
            "Activity review notification sent to %s for activity %s",
            engineer_email,
            activity.pk,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to send activity review notification for activity %s",
            activity.pk,
        )
        return False
    







from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="Site Checkbook Email Test",
    message="Congratulations! Your Django email configuration is working.",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["godwinsenwin@gmail.com"],
    fail_silently=False,
)