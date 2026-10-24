from apps.api.serializers import TagSerializer
from apps.recipes.models import Tag
from rest_framework import permissions, viewsets


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [permissions.AllowAny]