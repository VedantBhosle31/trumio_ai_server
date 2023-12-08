from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("resume", views.pdf_upload_view, name="resume_upload"),
    path("github_info/<str:username>", views.get_github_info, name="github_info_extractor"),
    path("codeforce_info/<str:username>", views.get_codefore_info, name="codeforce_info_extractor"),
    path("get_rel_teams/<int:pid>", views.get_relevant_teams, name="get_relevant_profile"),
    path("get-rel-projects/<int:sid>", views.get_preferred_projects, name="get_relevant_projects"),
    path("create_team", views.create_team, name="create-team")
]