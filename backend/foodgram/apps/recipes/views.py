from apps.recipes.models import Recipe
from django.shortcuts import get_object_or_404, redirect


def short_link_redirect(request, id):
    recipe = get_object_or_404(Recipe, pk=id)
    return redirect(f'/recipes/{recipe.pk}/')
