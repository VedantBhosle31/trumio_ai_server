from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("resume", views.pdf_upload_view, name="resume_upload"),
    path("github_info/<str:username>", views.get_github_info, name="github_info_extractor")
]