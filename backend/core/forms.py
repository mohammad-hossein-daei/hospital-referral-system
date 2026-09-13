from django import forms
from django.db import transaction

from .models import Doctor
from accounts.models import User


class DoctorAdminForm(forms.ModelForm):

    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
    )

    first_name = forms.CharField(
        label="نام",
        max_length=150,
    )

    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=150,
    )

    email = forms.EmailField(
        label="ایمیل",
        required=False,
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput,
        required=False,
        help_text="در حالت ویرایش، خالی بگذارید تا رمز قبلی تغییر نکند.",
    )

    class Meta:
        model = Doctor
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "medical_code",
            "specialty",
            "phone",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields["username"].initial = user.username
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
        else:
            self.fields["password"].required = True

    def clean_username(self):
        username = self.cleaned_data["username"]

        qs = User.objects.filter(username=username)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)

        if qs.exists():
            raise forms.ValidationError("این نام کاربری قبلاً استفاده شده است.")

        return username

    @transaction.atomic
    def save(self, commit=True):
        doctor = super().save(commit=False)

        is_new = doctor.pk is None

        if is_new:
            user = User(role=User.Role.DOCTOR)
        else:
            user = doctor.user

        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.role = User.Role.DOCTOR

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        doctor.user = user

        if commit:
            doctor.save()

        return doctor