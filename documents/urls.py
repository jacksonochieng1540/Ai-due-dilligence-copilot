from django.urls import path

from . import views_web

app_name = "documents"

urlpatterns = [
    path("upload/", views_web.upload_document, name="upload"),
    path("", views_web.document_list, name="list"),
    path("<int:pk>/", views_web.document_detail, name="detail"),
]
