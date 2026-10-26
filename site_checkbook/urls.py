
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "site_checkbook"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="site_checkbook/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("", views.dashboard, name="dashboard"),

    path(
        "activities/new/",
        views.create_activity,
        name="create_activity",
    ),

    path(
        "activities/<int:pk>/",
        views.activity_detail,
        name="activity_detail",
    ),

    path(
        "activities/<int:pk>/review/",
        views.review_activity,
        name="review_activity",
    ),

    path(
        "reviews/",
        views.review_queue,
        name="review_queue",
    ),

    path(
    "projects/",
    views.project_list,
    name="project_list",
    ),

    path(
        "projects/new/",
        views.create_project,
        name="create_project",
    ),

    path(
    "activities/<int:pk>/edit/",
    views.edit_activity,
    name="edit_activity",
    ),

    path(
    "activities/<int:activity_id>/delete/",
    views.delete_activity,
    name="delete_activity",
    ),

    path(
    "checklists/submit/", 
    views.create_checklist_submission,
    name="create_checklist",
    ),
    
    path(
        "checklists/manage/",
        views.manage_checklists,
        name="manage_checklists",
    ),
    path(
        "checklists/departments/new/",
        views.create_department,
        name="create_department",
    ),
    path(
        "checklists/new/",
        views.create_checklist_frontend,
        name="create_checklist_frontend",
    ),
    path(
    "projects/<int:pk>/edit/",
    views.edit_project,
    name="edit_project",
    ),

    path(
    "checklists/review/",
    views.checklist_review_queue,
    name="checklist_review_queue",
    ),
    path(
        "checklists/review/<int:submission_id>/",
        views.checklist_review_detail,
        name="checklist_review_detail",
    ),
    path(
        "checklists/review/<int:submission_id>/action/",
        views.review_checklist_submission,
        name="review_checklist_submission",
    ),

    path(
        "checklists/<int:submission_id>/edit/",
        views.edit_checklist_submission,
        name="edit_checklist_submission",
    ),


    
]
 