import base64

from apps.recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from apps.users.models import User
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from apps.recipes.models import MIN_AMOUNT_OF_INGREDIENTS


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
        except ValueError:
            raise serializers.ValidationError(
                'Не удалось декодировать данные изображения: '
                'часть строки после ";base64," '
                'должна быть корректной строкой base64.'
            )
        return super().to_internal_value(
            ContentFile(decoded, name=f'temp.{ext}')
        )


class CustomUserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('avatar',)


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


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [RecipeIngredient(recipe=recipe, ingredient=i['id'], amount=i['amount']) for i in ingredients]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe
