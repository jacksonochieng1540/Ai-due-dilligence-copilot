from django.urls import path

from . import view_web as views_web

app_name = "analysis"

urlpatterns = [
    path("", views_web.session_list, name="session_list"),
    path("sessions/new/", views_web.session_create, name="session_create"),
    path("sessions/<int:pk>/", views_web.session_detail, name="session_detail"),
]
