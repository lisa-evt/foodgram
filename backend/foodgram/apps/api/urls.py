from apps.api.views import (IngredientViewSet, RecipeViewSet, SubscribeView,
                            SubscriptionsView, TagViewSet, UserAvatarView)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = router.urls + [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarView.as_view(), name='avatars'),
    path('users/subscriptions/', SubscriptionsView.as_view()),
    path('users/<int:id>/subscribe/', SubscribeView.as_view()),
]
