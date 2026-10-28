from apps.api.views import TagViewSet, IngredientViewSet, UserViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = router.urls
