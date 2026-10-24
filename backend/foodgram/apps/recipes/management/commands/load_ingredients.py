import csv
import json
from pathlib import Path

from apps.recipes.models import Ingredient
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

FIELDS = ('name', 'measurement_unit')


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV или JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            raise CommandError(f'Файл не найден: {path}')

        with open(path, encoding='utf-8') as file:
            if path.suffix == '.csv':
                rows = list(csv.DictReader(file, fieldnames=FIELDS))
            elif path.suffix == '.json':
                rows = json.load(file)
            else:
                raise CommandError('Поддерживаются только .csv и .json')

        ingredients = []
        for number, row in enumerate(rows, start=1):
            ingredient = Ingredient(**row)
            try:
                ingredient.full_clean(validate_unique=False)
            except ValidationError as error:
                self.stdout.write(self.style.WARNING(
                    f'Строка {number} пропущена: {error}'
                ))
                continue
            ingredients.append(ingredient)

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'Обработано записей: {len(ingredients)}'
        ))