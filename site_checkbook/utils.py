from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from site_checkbook.forms import User

def send_submission_notification(submission, request):

    supervisor_emails = User.objects.filter(
        groups__name="Supervisor",
        is_active=True
    ).exclude(email="").values_list("email", flat=True)

    hr_emails = User.objects.filter(
        groups__name="HR",
        is_active=True
    ).exclude(email="").values_list("email", flat=True)

    recipients = list(set(
        list(supervisor_emails) + list(hr_emails)
    ))

    review_url = request.build_absolute_uri(
        reverse(
            "site_checkbook:checklist_review_detail",
            args=[submission.pk]
        )
    )

    if recipients:
        send_mail(
            subject="New Site Checklist Submitted",
            message=f"""
A new site checklist has been submitted.

Engineer: {submission.engineer.username}
Project: {submission.project.name}
Checklist: {submission.checklist.title}

Please review the submission using this link:

{review_url}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )