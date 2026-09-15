from rest_framework.permissions import BasePermission


class IsReactAdmin(BasePermission):
    """
    فقط سوپرادمین‌های سیستم اجازه دسترسی به
    APIهای پنل React Admin را دارند.

    نکته:
    is_superuser=True  → دسترسی دارد
    is_staff=False     → همچنان دسترسی API دارد
    """

    message = "شما دسترسی به پنل مدیریت را ندارید."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
            and request.user.is_active
        )