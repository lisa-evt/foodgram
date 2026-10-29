import base64
from apps.recipes.models import Tag, Ingredient
from apps.users.models import User
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer


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
