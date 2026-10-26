
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
    my_checklist_submissions = (
        ChecklistSubmission.objects
        .filter(engineer=user)
        .select_related("checklist", "project")
        .order_by("-inspection_date", "-pk")[:10]
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
        "my_checklist_submissions": my_checklist_submissions,
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
def create_checklist_submission(request, submission_id=None):
    """Create a checklist or correct a checklist returned by HR."""

    is_post = request.method == "POST"
    editing = submission_id is not None

    if editing:
        submission = get_object_or_404(
            ChecklistSubmission,
            pk=submission_id,
            engineer=request.user,
            status="returned",
        )
    else:
        submission = None

    submission_form = ChecklistSubmissionForm(
        request.POST if is_post else None,
        instance=submission,
        user=request.user,
    )

    if editing:
        submission_form.fields["checklist"].disabled = True

    checklist = submission.checklist if editing else None
    response_forms = []

    if is_post and not editing:
        checklist_id = request.POST.get("checklist")
        if checklist_id:
            checklist = Checklist.objects.filter(
                pk=checklist_id,
                is_active=True,
                department__is_active=True,
            ).first()
    elif not is_post and not editing:
        checklist_id = request.GET.get("checklist")
        if checklist_id:
            checklist = Checklist.objects.filter(
                pk=checklist_id,
                is_active=True,
                department__is_active=True,
            ).first()

    questions = (
        list(checklist.questions.all().order_by("order", "id"))
        if checklist else []
    )

    existing_responses = {
        response.question_id: response
        for response in ChecklistResponse.objects.filter(
            submission=submission
        )
    } if editing else {}

    if is_post and "load_checklist" in request.POST and not editing:
        if not submission_form.is_valid():
            messages.error(request, "Please check the inspection details.")
        elif not checklist:
            messages.error(request, "Please select a valid, active checklist.")
        elif not questions:
            messages.warning(
                request,
                "This checklist has no questions yet. Please contact HR.",
            )

    bind_answers = is_post and "submit_checklist" in request.POST

    for question in questions:
        response_form = ChecklistResponseForm(
            request.POST if bind_answers else None,
            instance=existing_responses.get(question.pk),
            prefix=f"question_{question.pk}",
        )
        response_form.fields["answer"].required = question.is_required
        response_forms.append((question, response_form))

    if bind_answers:
        if not submission_form.is_valid():
            messages.error(
                request,
                "Please correct the inspection details before submitting.",
            )
        elif not checklist:
            messages.error(
                request,
                "Please select a valid checklist and load its questions.",
            )
        elif (
            submission_form.cleaned_data["checklist"].pk != checklist.pk
        ):
            messages.error(
                request,
                "The selected checklist does not match the loaded questions. "
                "Please load the questions again.",
            )
        elif not response_forms:
            messages.error(
                request,
                "This checklist has no questions to submit.",
            )
        elif all(form.is_valid() for _, form in response_forms):
            try:
                with transaction.atomic():
                    saved_submission = submission_form.save(commit=False)

                    if not editing:
                        saved_submission.engineer = request.user

                    saved_submission.status = "submitted"
                    saved_submission.review_comments = ""
                    saved_submission.reviewed_at = None
                    saved_submission.save()

                    for question, response_form in response_forms:
                        response = response_form.save(commit=False)
                        response.submission = saved_submission
                        response.question = question
                        response.save()

                messages.success(
                    request,
                    "Your checklist has been submitted successfully for HR review.",
                )
                return redirect("site_checkbook:dashboard")

            except Exception:
                messages.error(
                    request,
                    "The checklist could not be saved. Please try again "
                    "and check the server error log if the problem continues.",
                )
        else:
            messages.error(
                request,
                "Please answer all required questions before submitting.",
            )

    return render(
        request,
        "site_checkbook/checklist_submission_form.html",
        {
            "submission_form": submission_form,
            "checklist": checklist,
            "response_forms": response_forms,
            "submission": submission,
            "is_editing": editing,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": can_manage_projects(request.user),
        },
    )


@login_required
def edit_checklist_submission(request, submission_id):
    """Open a returned checklist for correction."""
    return create_checklist_submission(request, submission_id=submission_id)




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
    """
    Show engineers' submitted checklists to HR and Supervisors.
    """
    if not is_hr_reviewer(request.user):
        messages.error(
            request,
            "You do not have permission to review inspection checklists."
        )
        return redirect("site_checkbook:dashboard")

    submissions = (
        ChecklistSubmission.objects
        .select_related(
            "checklist",
            "engineer",
            "project",
        )
        .order_by("-submitted_at", "-inspection_date", "-pk")
    )

    status_filter = request.GET.get("status", "submitted")

    valid_statuses = {"submitted", "reviewed", "returned", "all"}

    if status_filter not in valid_statuses:
        status_filter = "submitted"

    if status_filter != "all":
        submissions = submissions.filter(status=status_filter)

    context = {
        "submissions": submissions,
        "status_filter": status_filter,
        "pending_count": ChecklistSubmission.objects.filter(
            status="submitted"
        ).count(),
        "reviewed_count": ChecklistSubmission.objects.filter(
            status="reviewed"
        ).count(),
        "returned_count": ChecklistSubmission.objects.filter(
            status="returned"
        ).count(),
    }

    return render(
        request,
        "site_checkbook/checklist_review_queue.html",
        context,
    )


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