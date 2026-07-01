from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DueDiligenceSessionViewSet

router = DefaultRouter()
router.register(r"sessions", DueDiligenceSessionViewSet, basename="session")

urlpatterns = [
    path("", include(router.urls)),
]
