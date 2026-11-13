from apps.api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                            UserAvatarView, SubscribeView, SubscriptionsView)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = router.urls + [
    path('users/subscriptions/', SubscriptionsView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarView.as_view(), name='avatars'),
    path('users/<int:id>/subscribe/', SubscribeView.as_view()),
    path('', include('djoser.urls')),
]
