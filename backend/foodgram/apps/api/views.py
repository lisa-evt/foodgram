from apps.api.serializers import TagSerializer, IngredientSerializer, UserSignUpSerializer
from apps.recipes.models import Tag, Ingredient
from apps.api.filters import IngredientFilter
from rest_framework import permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import mixins, viewsets


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


def get_permissions(self):
    if self.action in ('list', 'create'):
        return [AllowAny()]
    return [IsAuthenticated()]

class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSignUpSerializer
    permission_classes = (permissions.AllowAny,)