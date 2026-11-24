from apps.api.views import (IngredientViewSet, RecipeViewSet,
                            SubscriptionsView, TagViewSet, UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet)

urlpatterns = [
    path('users/subscriptions/', SubscriptionsView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
