from apps.api.filters import IngredientFilter
from apps.api.permissions import IsAuthorOrReadOnly
from apps.api.serializers import (AvatarSerializer, IngredientSerializer,
                                  RecipeSerializer, RecipeShortSerializer,
                                  TagSerializer, UserWithRecipesSerializer)
from apps.recipes.models import (Favorite, Ingredient, Recipe,
                                 RecipeIngredient, ShoppingCart, Tag)
from apps.users.models import Subscription
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_or_remove(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                RecipeShortSerializer(
                    recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        deleted, _ = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепта нет в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove(request, pk, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )
        if not ingredients:
            return Response(
                {'errors': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        lines = [
            '{} ({}) — {}'.format(
                item['ingredient__name'],
                item['ingredient__measurement_unit'],
                item['total'],
            )
            for item in ingredients
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
        methods=['get'],
        url_path='get-link',
        permission_classes=(permissions.AllowAny,),
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        relative_url = reverse('short_link', kwargs={'id': recipe.pk})
        return Response({
            'short-link': request.build_absolute_uri(relative_url)
        })


class SubscribeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            return Response(
                {'errors': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Subscription.objects.get_or_create(
            user=request.user,
            author=author,
        )
        if not created:
            return Response(
                {'errors': 'Вы уже подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            UserWithRecipesSerializer(
                author,
                context={'request': request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, id):
        author = get_object_or_404(User, pk=id)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).delete()
        if not deleted:
            return Response(
                {'errors': 'Вы не были подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(viewsets.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserWithRecipesSerializer

    def get_queryset(self):
        return (
            User.objects
            .filter(subscribers__user=self.request.user)
            .prefetch_related('recipes')
            .order_by('id')
        )
