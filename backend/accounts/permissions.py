from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    فقط کاربرانی با role=admin یا سوپرادمین دسترسی دارن
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role == user.Role.ADMIN)
        )