import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV или JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            raise CommandError(f'Файл не найден: {path}')

        if path.suffix == '.csv':
            with open(path, encoding='utf-8') as file:
                rows = [
                    {'name': name, 'measurement_unit': unit}
                    for name, unit in csv.reader(file)
                ]
        elif path.suffix == '.json':
            with open(path, encoding='utf-8') as file:
                rows = json.load(file)
        else:
            raise CommandError('Поддерживаются только .csv и .json')

        Ingredient.objects.bulk_create(
            [Ingredient(**row) for row in rows],
            ignore_conflicts=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Обработано записей: {len(rows)}')
        )