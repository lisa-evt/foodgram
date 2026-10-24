from apps.api.views import TagViewSet
from django.urls import path

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')

urlpatterns = router.urls
