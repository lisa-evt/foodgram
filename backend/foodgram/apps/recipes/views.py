from django.shortcuts import get_object_or_404, redirect
from apps.recipes.models import Recipe


def short_link_redirect(request, id):
    recipe = get_object_or_404(Recipe, pk=id)
    return redirect(f'/recipes/{recipe.pk}/')
