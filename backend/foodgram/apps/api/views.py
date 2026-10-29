from apps.api.serializers import TagSerializer, IngredientSerializer, AvatarSerializer
from apps.recipes.models import Tag, Ingredient
from apps.api.filters import IngredientFilter
from rest_framework import permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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


class UserAvatarView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        old_avatar = request.user.avatar.name
        serializer.save()
        if old_avatar:
            request.user.avatar.storage.delete(old_avatar)
        return Response(serializer.data)

    def delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
