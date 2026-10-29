from apps.api.views import TagViewSet, IngredientViewSet, UserAvatarView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = router.urls + [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarView.as_view(), name='avatars')
]
