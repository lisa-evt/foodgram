from apps.api.views import TagViewSet, IngredientViewSet, UserViewSet, LoginView, LogoutView
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = router.urls + [
    path('auth/token/login/', LoginView.as_view(), name='login'),
    path('auth/token/logout/', LogoutView.as_view(), name='logout'),
]
