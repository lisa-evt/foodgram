import base64
import string

from apps.recipes.models import (MIN_AMOUNT_OF_INGREDIENTS, Favorite,
                                 Ingredient, Recipe, RecipeIngredient,
                                 ShoppingCart, Tag)
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers


User = get_user_model()
ASCII_DIGITS = frozenset(string.digits)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if not isinstance(data, str):
            return super().to_internal_value(data)
        if not data.startswith('data:image') or ';base64,' not in data:
            raise serializers.ValidationError(
                'Неверный формат изображения. '
                'Ожидается: data:image/<тип>;base64,<данные>.'
            )
        header, imgstr = data.split(';base64,', 1)
        ext = header.split('/')[-1]
        try:
            decoded = base64.b64decode(imgstr, validate=True)
        except ValueError as exc:
            raise serializers.ValidationError(
                'Не удалось декодировать данные изображения: '
                'часть строки после ";base64," '
                'должна быть корректной строкой base64.'
            ) from exc
        return super().to_internal_value(
            ContentFile(decoded, name=f'temp.{ext}')
        )


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=obj).exists()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('avatar', 'is_subscribed')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT_OF_INGREDIENTS)


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один ингредиент.'
            )
        for item in value:
            if 'id' not in item:
                raise serializers.ValidationError(
                    'У каждого ингредиента должен быть указан id.'
                )
        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate(self, attrs):
        for field in ('tags', 'ingredients'):
            if field not in attrs:
                raise serializers.ValidationError(
                    {field: 'Обязательное поле.'}
                )
        return attrs

    def _create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self._create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self._create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        data['ingredients'] = RecipeIngredientReadSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, author):
        recipes = author.recipes.all()
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit and set(limit) <= ASCII_DIGITS:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data
