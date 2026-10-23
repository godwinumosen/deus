
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProjectForm, SiteActivityForm
from .models import ActivityPhoto, Project, SiteActivity
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