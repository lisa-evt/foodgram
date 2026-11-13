from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework import permissions


class IsAuthorOrReadOnly(
    permissions.IsAuthenticatedOrReadOnly
):
    """Дает доступ к изменению данных только автору"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class UserPermission(CurrentUserOrAdminOrReadOnly):
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return super().has_permission(request, view)
