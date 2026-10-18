from django.db import models
from django.db.models import UniqueConstraint


TAG_NAME_MAX_LENGTH = 32
INGREDIENT_NAME_MAX_LENGTH = 128
RECIPE_NAME_MAX_LENGTH = 256
MEASUREMENT_NAME_MAX_LENGTH = 64


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    slug = models.SlugField(max_length=TAG_NAME_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=MEASUREMENT_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'