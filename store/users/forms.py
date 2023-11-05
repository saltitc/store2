import uuid
from datetime import timedelta
from django.utils.timezone import now

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)


from .models import User, EmailVerification


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password")

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control py-4",
                "placeholder": "Введите имя пользователя",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-4", "placeholder": "Введите пароль"}
        )
    )


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "gender",
            "email",
            "phone",
            "password1",
            "password2",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control py-4", "placeholder": "Введите имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control py-4", "placeholder": "Введите фамилию"}
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control py-4",
                    "placeholder": "Введите имя пользователя",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control py-4",
                    "placeholder": "Введите адрес эл. почты",
                }
            ),
            "gender": forms.Select(
                choices=User.GENDER_CHOICES,
                attrs={"class": "form-control py-4", "style": "height: 50px;"},
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control py-4", "placeholder": "8-999-999-99-99"}
            ),
        }

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-4", "placeholder": "Введите пароль"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-4", "placeholder": "Подтвердите пароль"}
        )
    )

    def save(self, commit=True):
        user = super().save(commit=True)
        expiration = now() + timedelta(hours=48)
        record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
        record.send_verification_email()
        return user


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control py-4"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control py-4"})
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "custom-file-input"}), required=False
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control py-4", "readonly": True})
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={"class": "form-control py-4", "readonly": True})
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control py-4"})
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "image", "username", "email", "phone")
