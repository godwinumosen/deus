
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ChecklistResponseForm, ChecklistSubmissionForm, ProjectForm, SiteActivityForm
from .models import ActivityPhoto, Checklist, Project, SiteActivity
from .permissions import can_manage_projects, is_hr_reviewer


@login_required
def dashboard(request):
    user = request.user
    reviewer = is_hr_reviewer(user)

    if reviewer:
        projects = Project.objects.filter(is_active=True)
        activities = SiteActivity.objects.select_related(
            "project", "engineer"
        )
    else:
        projects = Project.objects.filter(
            engineers=user,
            is_active=True,
        ).distinct()

        activities = SiteActivity.objects.filter(
            engineer=user,
            project__in=projects,
        ).select_related("project", "engineer")

    activities = activities.order_by("-activity_date", "-created_at")
    today = timezone.localdate()

    context = {
        "projects": projects,
        "activities": activities[:10],
        "total_projects": projects.count(),
        "total_activities": activities.count(),
        "pending_reviews": activities.filter(
            status="submitted"
        ).count(),
        "today_activities": activities.filter(
            activity_date=today
        ).count(),
        "is_reviewer": reviewer,
        "can_manage_projects": can_manage_projects(user),
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
    """Allow an engineer to complete and submit a checklist."""

    is_post = request.method == "POST"

    submission_form = ChecklistSubmissionForm(
        request.POST if is_post else None,
        user=request.user,
    )

    checklist = None
    response_forms = []

    # Identify the checklist selected by the engineer.
    checklist_id = (
        request.POST.get("checklist")
        if is_post
        else request.GET.get("checklist")
    )

    if checklist_id:
        checklist = Checklist.objects.filter(
            pk=checklist_id,
            is_active=True,
            department__is_active=True,
        ).first()

    # Prepare the question forms for the selected checklist.
    if checklist:
        questions = checklist.questions.all().order_by("order", "id")

        for question in questions:
            response_form = ChecklistResponseForm(
                request.POST if is_post else None,
                prefix=f"question_{question.pk}",
            )
            response_form.fields["answer"].required = (
                question.is_required
            )
            response_forms.append((question, response_form))

    # Handle the Load Checklist Questions button.
    if is_post and "load_checklist" in request.POST:
        if not checklist:
            messages.error(
                request,
                "Please select a valid, active checklist.",
            )

        elif not checklist.questions.exists():
            messages.warning(
                request,
                "This checklist has no questions yet. Please ask HR to add questions.",
            )

        # Render the page with the selected checklist and its questions.
        return render(
            request,
            "site_checkbook/checklist_submission_form.html",
            {
                "submission_form": submission_form,
                "checklist": checklist,
                "response_forms": response_forms,
                "is_reviewer": is_hr_reviewer(request.user),
                "can_manage_projects": can_manage_projects(
                    request.user
                ),
            },
        )

    # Handle Submit Checklist for Review.
    if is_post:
        if not submission_form.is_valid():
            pass

        elif not checklist:
            messages.error(
                request,
                "Please select and load a valid checklist before submitting.",
            )

        elif (
            submission_form.cleaned_data["checklist"].pk
            != checklist.pk
        ):
            messages.error(
                request,
                "The selected checklist does not match its questions. Please load it again.",
            )

        else:
            all_responses_valid = True

            for question, response_form in response_forms:
                if not response_form.is_valid():
                    all_responses_valid = False

            if all_responses_valid:
                with transaction.atomic():
                    submission = submission_form.save(commit=False)
                    submission.engineer = request.user
                    submission.status = "submitted"
                    submission.save()

                    for question, response_form in response_forms:
                        answer = response_form.cleaned_data.get(
                            "answer"
                        )
                        comments = response_form.cleaned_data.get(
                            "comments"
                        )

                        # Save an answer or comments, including answers
                        # that might be false-like values such as 0.
                        if answer not in (None, "") or comments:
                            response = response_form.save(
                                commit=False
                            )
                            response.submission = submission
                            response.question = question
                            response.save()

                messages.success(
                    request,
                    "Your checklist has been submitted successfully for HR review.",
                )
                return redirect("site_checkbook:dashboard")

    return render(
        request,
        "site_checkbook/checklist_submission_form.html",
        {
            "submission_form": submission_form,
            "checklist": checklist,
            "response_forms": response_forms,
            "is_reviewer": is_hr_reviewer(request.user),
            "can_manage_projects": can_manage_projects(
                request.user
            ),
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
