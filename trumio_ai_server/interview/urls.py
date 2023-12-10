from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("student/resume", views.pdf_upload_view, name="resume_upload"),
    path("student/github_info/<str:username>", views.get_github_info, name="github_info_extractor"),
    path("student/codeforce_info/<str:username>", views.get_codefore_info, name="codeforce_info_extractor"),
    path("projects/get_rel_teams/<str:pid>", views.get_relevant_teams, name="get_relevant_profile"),
    path("students/get-rel-projects/<str:sid>", views.get_preferred_projects, name="get_relevant_projects"),
    path("teams/create", views.create_team, name="create-team"),
    path("profile/get_scores", views.get_scores, name="get_score_and_recommend"),
    path("projects/create", views.create_project, name="create_project")
]


