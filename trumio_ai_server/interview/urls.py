from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("students/resume", views.pdf_upload_view, name="resume_upload"),
    path("students/github_info/<str:username>", views.get_github_info, name="github_info_extractor"),
    path("students/codeforce_info/<str:username>", views.get_codefore_info, name="codeforce_info_extractor"),
    path("projects/get_rel_teams/<str:pid>", views.get_relevant_teams, name="get_relevant_profile"),
    path("students/get_rel_projects/<str:sid>", views.get_relevant_projects, name="get_relevant_projects"),
    path("teams/get_rel_projects/<str:tid>", views.get_relevant_projects_for_team, name="get_relevant_projects"),
    path("teams/create", views.create_team, name="create-team"),
    path("students/get_scores", views.get_scores, name="get_score_and_recommend"),
    path("projects/create", views.create_project, name="create_project")
]


