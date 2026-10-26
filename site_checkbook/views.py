
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ChecklistResponseForm, ChecklistSubmissionForm, ProjectForm, SiteActivityForm
from .models import ActivityPhoto, Checklist, ChecklistResponse, ChecklistSubmission, Project, SiteActivity
from .permissions import can_manage_projects, is_hr_reviewer


@login_required
def dashboard(request):
    user = request.user
    reviewer = is_hr_reviewer(user)

    if reviewer:
        projects = Project.objects.filter(is_active=True)

        activities = SiteActivity.objects.select_related(
            "project",
            "engineer",
        )
    else:
        projects = Project.objects.filter(
            engineers=user,
            is_active=True,
        ).distinct()

        activities = SiteActivity.objects.filter(
            engineer=user,
            project__in=projects,
        ).select_related(
            "project",
            "engineer",
        )

    activities = activities.order_by(
        "-activity_date",
        "-created_at",
    )

    today = timezone.localdate()

    # Active departments with active checklists only.
    checklist_categories = (
        Department.objects
        .filter(
            is_active=True,
            checklists__is_active=True,
        )
        .distinct()
        .prefetch_related("checklists")
        .order_by("name")
    )

    context = {
        "projects": projects,
        "activities": activities[:10],
        "total_projects": projects.count(),
        "total_activities": activities.count(),
        "pending_reviews": activities.filter(
            status="submitted",
        ).count(),
        "today_activities": activities.filter(
            activity_date=today,
        ).count(),
        "is_reviewer": reviewer,
        "can_manage_projects": can_manage_projects(user),
        "checklist_categories": checklist_categories,
    }

    return render(
        request,
        "site_checkbook/dashboard.html",
        context,
    )



@login_required
def create_activity(request):
    if request.method == "POST":
        form = SiteActivityForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():
            activity = form.save(commit=False)
            activity.engineer = request.user
            activity.status = "submitted"
            activity.save()

            for image in request.FILES.getlist("photos"):
                ActivityPhoto.objects.create(
                    activity=activity,
                    image=image,
                )

            messages.success(
                request,
                "Your site activity report has been submitted.",
            )
            return redirect("site_checkbook:dashboard")
    else:
        form = SiteActivityForm(user=request.user)

    return render(
        request,
        "site_checkbook/create_activity.html",
        {
            "form": form,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": can_manage_projects(request.user),
        },
    )


@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(
        SiteActivity.objects.select_related(
            "project", "engineer"
        ).prefetch_related("photos"),
        pk=pk,
    )

    reviewer = is_hr_reviewer(request.user)

    if not reviewer and activity.engineer_id != request.user.pk:
        raise PermissionDenied

    return render(
        request,
        "site_checkbook/activity_detail.html",
        {
            "activity": activity,
            "is_reviewer": reviewer,
            "can_manage_projects": can_manage_projects(request.user),
        },
    )





@login_required
@require_POST
def review_activity(request, pk):
    if not is_hr_reviewer(request.user):
        raise PermissionDenied

    activity = get_object_or_404(SiteActivity, pk=pk)

    if activity.status != "submitted":
        messages.warning(
            request,
            "Only submitted reports can be reviewed.",
        )
        return redirect(
            "site_checkbook:activity_detail",
            pk=activity.pk,
        )

    action = request.POST.get("action")

    if action == "approve":
        activity.status = "reviewed"
        activity.save(update_fields=["status", "updated_at"])

        messages.success(
            request,
            "Report marked as reviewed.",
        )

    elif action == "return":
        activity.status = "returned"
        activity.save(update_fields=["status", "updated_at"])

        messages.warning(
            request,
            "Report returned for correction.",
        )

    else:
        messages.error(request, "Invalid review action.")

    return redirect(
        "site_checkbook:activity_detail",
        pk=activity.pk,
    )


@login_required
def project_list(request):
    if not can_manage_projects(request.user):
        raise PermissionDenied

    projects = Project.objects.prefetch_related("engineers").all()

    return render(
        request,
        "site_checkbook/project_list.html",
        {
            "projects": projects,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": True,
        },
    )


@login_required
def create_project(request):
    if not can_manage_projects(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Project created and engineers assigned successfully.",
            )

            return redirect("site_checkbook:project_list")
    else:
        form = ProjectForm()

    return render(
        request,
        "site_checkbook/project_form.html",
        {
            "form": form,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": True,
        },
    )



@login_required
def edit_activity(request, pk):
    reviewer = is_hr_reviewer(request.user)

    activity = get_object_or_404(
        SiteActivity.objects.select_related("project", "engineer"),
        pk=pk,
    )

    # Engineers can edit only their own draft or returned reports.
    if not reviewer:
        if activity.engineer_id != request.user.pk:
            raise PermissionDenied

        if activity.status not in ["draft", "returned"]:
            messages.error(
                request,
                "You can only edit draft reports or reports returned for correction.",
            )
            return redirect(
                "site_checkbook:activity_detail",
                pk=activity.pk,
            )

    if request.method == "POST":
        form = SiteActivityForm(
            request.POST,
            request.FILES,
            instance=activity,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your report has been updated successfully."
                if not reviewer
                else "The site report has been corrected successfully.",
            )

            return redirect(
                "site_checkbook:activity_detail",
                pk=activity.pk,
            )
    else:
        form = SiteActivityForm(
            instance=activity,
            user=request.user,
        )

    return render(
        request,
        "site_checkbook/edit_activity.html",
        {
            "form": form,
            "activity": activity,
            "is_reviewer": reviewer,
            "can_manage_projects": can_manage_projects(request.user),
        },
    )




@login_required
def review_queue(request):
    if not is_hr_reviewer(request.user):
        raise PermissionDenied

    activities = (
        SiteActivity.objects
        .select_related("project", "engineer")
        .order_by("-activity_date", "-created_at")
    )

    context = {
        "activities": activities,
        "pending_count": activities.filter(status="submitted").count(),
        "is_reviewer": True,
        "can_manage_projects": can_manage_projects(request.user),
    }

    return render(
        request,
        "site_checkbook/review_queue.html",
        context,
    )


@login_required
@require_POST
def delete_activity(request, activity_id):
    if not is_hr_reviewer(request.user):
        messages.error(request, "You are not allowed to delete reports.")
        return redirect("site_checkbook:dashboard")

    activity = get_object_or_404(
        SiteActivity,
        pk=activity_id,
    )

    activity.delete()

    messages.success(request, "Daily report deleted successfully.")

    return redirect("site_checkbook:reviews")



@login_required
def create_checklist_submission(request):
    is_post = request.method == "POST"

    # Preserve the selected checklist on GET and POST.
    checklist_id = (
        request.POST.get("checklist")
        if is_post
        else request.GET.get("checklist")
    )

    submission_form = ChecklistSubmissionForm(
        request.POST if is_post else None,
        user=request.user,
        initial={"checklist": checklist_id} if checklist_id else None,
    )

    checklist = None
    response_forms = []

    if checklist_id:
        checklist = Checklist.objects.filter(
            pk=checklist_id,
            is_active=True,
            department__is_active=True,
        ).first()

        if checklist is None:
            messages.error(
                request,
                "The selected checklist is unavailable or inactive.",
            )
            checklist_id = None

    if checklist:
        questions = checklist.questions.all().order_by(
            "order",
            "id",
        )

        for question in questions:
            prefix = f"question_{question.pk}"

            response_form = ChecklistResponseForm(
                request.POST if is_post else None,
                prefix=prefix,
            )

            response_forms.append((question, response_form))

    # The Load Questions button only loads the selected checklist.
    if is_post and "load_checklist" in request.POST:
        if checklist is None:
            messages.error(
                request,
                "Please select an active checklist before loading questions.",
            )

        return render(
            request,
            "site_checkbook/create_checklist.html",
            {
                "submission_form": submission_form,
                "checklist": checklist,
                "response_forms": response_forms,
            },
        )

    # Save a completed inspection.
    if is_post and "submit_checklist" in request.POST:
        form_valid = submission_form.is_valid()

        if not checklist:
            messages.error(
                request,
                "Please select a valid checklist.",
            )
            form_valid = False
        elif (
            form_valid
            and submission_form.cleaned_data.get("checklist") != checklist
        ):
            messages.error(
                request,
                "The selected checklist does not match the submitted questions.",
            )
            form_valid = False

        responses_valid = True

        for question, response_form in response_forms:
            if not response_form.is_valid():
                responses_valid = False

        if not response_forms:
            messages.error(
                request,
                "This checklist has no questions and cannot be submitted.",
            )
            responses_valid = False

        if form_valid and responses_valid:
            with transaction.atomic():
                submission = submission_form.save(commit=False)
                submission.engineer = request.user
                submission.status = "submitted"
                submission.save()

                for question, response_form in response_forms:
                    answer = response_form.cleaned_data.get("answer")
                    comments = response_form.cleaned_data.get("comments", "")

                    ChecklistResponse.objects.create(
                        submission=submission,
                        question=question,
                        answer=answer,
                        comments=comments,
                    )

            messages.success(
                request,
                "Your inspection checklist has been submitted to HR for review.",
            )

            return redirect("site_checkbook:dashboard")

        messages.error(
            request,
            "Please correct the errors below before submitting your checklist.",
        )

    return render(
        request,
        "site_checkbook/create_checklist.html",
        {
            "submission_form": submission_form,
            "checklist": checklist,
            "response_forms": response_forms,
        },
    )



from django.forms import inlineformset_factory
from .models import Department, Checklist, ChecklistQuestion
from .permissions import is_hr_reviewer


ChecklistQuestionFormSet = inlineformset_factory(
    Checklist,
    ChecklistQuestion,
    fields=("question_text", "is_required", "order"),
    extra=3,
    can_delete=True,
)


@login_required
def manage_checklists(request):
    if not is_hr_reviewer(request.user):
        raise PermissionDenied

    departments = Department.objects.all().order_by("name")
    checklists = Checklist.objects.select_related(
        "department"
    ).prefetch_related("questions")

    return render(
        request,
        "site_checkbook/manage_checklists.html",
        {
            "departments": departments,
            "checklists": checklists,
            "is_reviewer": True,
            "can_manage_projects": can_manage_projects(request.user),
        },
    )


@login_required
def create_department(request):
    if not is_hr_reviewer(request.user):
        raise PermissionDenied

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            department, created = Department.objects.get_or_create(
                name=name,
                defaults={"description": description, "is_active": True},
            )
            if created:
                messages.success(request, "Department created.")
            else:
                messages.warning(request, "That department already exists.")
        else:
            messages.error(request, "Enter a department name.")

    return redirect("site_checkbook:manage_checklists")


@login_required
def create_checklist_frontend(request):
    if not is_hr_reviewer(request.user):
        raise PermissionDenied

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        department_id = request.POST.get("department")

        department = Department.objects.filter(
            pk=department_id,
            is_active=True,
        ).first() if department_id else None

        if not title or not department:
            messages.error(
                request,
                "Enter a checklist title and select an active department.",
            )
            return redirect("site_checkbook:manage_checklists")

        checklist = Checklist.objects.create(
            title=title,
            description=description,
            department=department,
            is_active=True,
        )

        question_texts = request.POST.getlist("question_text")
        required_values = request.POST.getlist("question_required")

        order = 1
        for index, text_value in enumerate(question_texts):
            text_value = text_value.strip()
            if text_value:
                ChecklistQuestion.objects.create(
                    checklist=checklist,
                    question_text=text_value,
                    is_required=str(index) in required_values,
                    order=order,
                )
                order += 1

        messages.success(request, "Checklist and questions created.")
        return redirect("site_checkbook:manage_checklists")

    return redirect("site_checkbook:manage_checklists")




@login_required
def edit_project(request, pk):
    if not can_manage_projects(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"Project {project.project_code} updated successfully.",
            )
            return redirect("site_checkbook:project_list")
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "site_checkbook/project_form.html",
        {
            "form": form,
            "project": project,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": True,
            "page_title": "Edit Project",
            "submit_text": "Save Changes",
        },
    )

def is_hr_reviewer(user):
    """
    Only HR, Supervisors and superusers can review engineer checklists.
    """
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name__in=["HR", "Supervisors"]).exists()
        )
    )


@login_required
def checklist_review_queue(request):
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists.",
        )
        return redirect("site_checkbook:dashboard")

    status_filter = request.GET.get("status", "submitted")

    if status_filter not in {
        "submitted",
        "reviewed",
        "returned",
        "all",
    }:
        status_filter = "submitted"

    submissions = ChecklistSubmission.objects.select_related(
        "checklist",
        "checklist__department",
        "engineer",
        "project",
    ).order_by("-pk")

    if status_filter != "all":
        submissions = submissions.filter(status=status_filter)

    context = {
        "submissions": submissions,
        "status_filter": status_filter,
        "pending_count": ChecklistSubmission.objects.filter(
            status="submitted",
        ).count(),
        "reviewed_count": ChecklistSubmission.objects.filter(
            status="reviewed",
        ).count(),
        "returned_count": ChecklistSubmission.objects.filter(
            status="returned",
        ).count(),
    }

    return render(
        request,
        "site_checkbook/checklist_review_queue.html",
        context,
    )


@login_required
def checklist_review_detail(request, submission_id):
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists.",
        )
        return redirect("site_checkbook:dashboard")

    submission = get_object_or_404(
        ChecklistSubmission.objects.select_related(
            "checklist",
            "checklist__department",
            "engineer",
            "project",
        ),
        pk=submission_id,
    )

    responses = ChecklistResponse.objects.filter(
        submission=submission,
    ).select_related(
        "question",
    ).order_by(
        "question__order",
        "question_id",
    )

    return render(
        request,
        "site_checkbook/checklist_review_detail.html",
        {
            "submission": submission,
            "responses": responses,
        },
    )


@login_required
@require_POST
def review_checklist_submission(request, submission_id):
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists.",
        )
        return redirect("site_checkbook:dashboard")

    submission = get_object_or_404(
        ChecklistSubmission,
        pk=submission_id,
    )

    action = request.POST.get("action")

    if action not in {"reviewed", "returned"}:
        messages.error(request, "Invalid review action.")
        return redirect(
            "site_checkbook:checklist_review_detail",
            submission_id=submission.pk,
        )

    submission.status = action
    submission.save(update_fields=["status"])

    if action == "reviewed":
        messages.success(
            request,
            "The engineer's checklist has been marked as reviewed.",
        )
    else:
        messages.warning(
            request,
            "The checklist has been returned to the engineer for correction.",
        )

    return redirect("site_checkbook:checklist_review_queue")



@login_required
def checklist_review_detail(request, submission_id):
    """
    Display one engineer's submitted checklist and its answers.
    """
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists."
        )
        return redirect("site_checkbook:dashboard")

    submission = get_object_or_404(
        ChecklistSubmission.objects.select_related(
            "checklist",
            "engineer",
            "project",
        ),
        pk=submission_id,
    )

    responses = (
        ChecklistResponse.objects
        .filter(submission=submission)
        .select_related("question")
        .order_by("question__order", "question_id")
    )

    context = {
        "submission": submission,
        "responses": responses,
    }

    return render(
        request,
        "site_checkbook/checklist_review_detail.html",
        context,
    )


@login_required
@require_POST
def review_checklist_submission(request, submission_id):
    """
    HR can mark a submission reviewed or return it for correction.
    """
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists."
        )
        return redirect("site_checkbook:dashboard")

    action = request.POST.get("action")
    review_comments = request.POST.get("review_comments", "").strip()

    submission = get_object_or_404(
        ChecklistSubmission.objects.select_related(
            "checklist",
            "engineer",
            "project",
        ),
        pk=submission_id,
    )

    if action not in {"reviewed", "returned"}:
        messages.error(request, "Invalid checklist review action.")
        return redirect(
            "site_checkbook:checklist_review_detail",
            submission_id=submission.pk,
        )

    if action == "returned" and not review_comments:
        messages.error(
            request,
            "Please explain what the engineer needs to correct before returning the checklist.",
        )
        return redirect(
            "site_checkbook:checklist_review_detail",
            submission_id=submission.pk,
        )

    with transaction.atomic():
        submission.status = action
        submission.review_comments = review_comments

        if action == "reviewed":
            submission.reviewed_at = timezone.now()
        else:
            submission.reviewed_at = None

        submission.save(
            update_fields=[
                "status",
                "review_comments",
                "reviewed_at",
            ]
        )

    if action == "reviewed":
        messages.success(
            request,
            "The inspection checklist has been marked as reviewed.",
        )
    else:
        messages.warning(
            request,
            "The inspection checklist has been returned to the engineer for correction.",
        )

    return redirect("site_checkbook:checklist_review_queue")