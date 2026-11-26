from apps.api.filters import IngredientFilter, RecipeFilterSet
from apps.api.pagination import LimitPageNumberPagination
from apps.api.permissions import IsAuthorOrReadOnly
from apps.api.serializers import (AvatarSerializer, FavoriteSerializer,
                                  IngredientSerializer, RecipeSerializer,
                                  ShoppingCartSerializer,
                                  SubscriptionSerializer, TagSerializer,
                                  UserWithRecipesSerializer)
from apps.recipes.models import (Favorite, Ingredient, Recipe,
                                 RecipeIngredient, ShoppingCart, Tag)
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

User = get_user_model()

AUTHENTICATED_ACTIONS = ('me', 'avatar', 'subscribe')
ADMIN_ONLY_ACTIONS = ('update', 'partial_update', 'destroy')


class ReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagViewSet(ReadOnlyViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class UserViewSet(DjoserUserViewSet):

    def get_permissions(self):
        if self.action in AUTHENTICATED_ACTIONS:
            return (IsAuthenticated(),)
        if self.action in ADMIN_ONLY_ACTIONS:
            return (IsAdminUser(),)
        return super().get_permissions()

    @action(detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=False, methods=('put', 'delete'), url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            old_avatar = user.avatar.name
            serializer.save()
            if old_avatar:
                user.avatar.storage.delete(old_avatar)
            return Response(serializer.data)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, **kwargs):
        author = self.get_object()
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'author': author.pk},
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = request.user.subscriptions.filter(
            author=author
        ).delete()
        if not deleted:
            raise ValidationError('Вы не были подписаны на этого автора.')
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        return super().get_queryset().with_user_flags(self.request.user)

    def _serialize_fresh(self, pk):
        recipe = self.get_queryset().get(pk=pk)
        return self.get_serializer(recipe).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            self._serialize_fresh(serializer.instance.pk),
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self._serialize_fresh(serializer.instance.pk))

    def _add_or_remove(self, request, model, serializer_class):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = serializer_class(
                data={'recipe': recipe.pk},
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            raise ValidationError('Рецепта нет в списке.')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove(request, Favorite, FavoriteSerializer)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(
            request, ShoppingCart, ShoppingCartSerializer
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcarts__user=request.user)
            .values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit'),
            )
            .annotate(total=Sum('amount'))
            .order_by('name')
        )
        if not ingredients:
            raise ValidationError('Корзина пуста.')
        lines = [
            '{name} ({measurement_unit}) — {total}'.format(**ingredient)
            for ingredient in ingredients
        ]
        response = HttpResponse(
            '\n'.join(lines), content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        url_path='get-link',
        permission_classes=(AllowAny,),
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        relative_url = reverse('short_link', kwargs={'id': recipe.pk})
        return Response({
            'short-link': request.build_absolute_uri(relative_url)
        })


class SubscriptionsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserWithRecipesSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return (
            User.objects
            .filter(subscribers__user=self.request.user)
            .prefetch_related('recipes')
            .order_by('id')
        )
