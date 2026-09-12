from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class NationalCodeBackend(ModelBackend):
    """
    احراز هویت با کد ملی و رمز عبور
    """
    def authenticate(self, request, national_code=None, password=None, **kwargs):
        if national_code is None or password is None:
            return None
        try:
            user = User.objects.get(national_code=national_code)
        except User.DoesNotExist:
            # اجرای هش پسورد برای جلوگیری از timing attack
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None