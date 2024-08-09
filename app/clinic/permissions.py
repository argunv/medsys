"""Permission classes for the clinic app."""
from django.http import HttpRequest
from rest_framework.permissions import BasePermission

from .config.levels import UserLevel


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.

    Attributes:
        request (HttpRequest): The request object.
        view (View): The view object.

    Returns:
        bool: True if the user is an admin user, False otherwise.
    """

    def has_permission(self, request: HttpRequest, _) -> bool:
        """Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            bool: True if the user is an admin user, False otherwise.
        """
        return request.user and request.user.user_level == UserLevel.SUPERUSER.value
