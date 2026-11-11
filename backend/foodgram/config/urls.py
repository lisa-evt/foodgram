"""URL configuration for foodgram project."""

from django.contrib import admin
from django.urls import include, path
from apps.recipes.views import short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('s/<int:id>/', short_link_redirect, name='short_link'),
]
