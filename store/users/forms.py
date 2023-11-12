from users.tasks import send_email_verification
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import password_validation
from django.conf import settings
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth import get_user_model

User = get_user_model()


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
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control py-4", "placeholder": "Введите пароль"}))
    recaptcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY, private_key=settings.RECAPTCHA_PRIVATE_KEY, label="ReCAPTCHA"
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
            "first_name": forms.TextInput(attrs={"class": "form-control py-4", "placeholder": "Введите имя"}),
            "last_name": forms.TextInput(attrs={"class": "form-control py-4", "placeholder": "Введите фамилию"}),
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
            "phone": forms.TextInput(attrs={"class": "form-control py-4", "placeholder": "8-999-999-99-99"}),
        }

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control py-4", "placeholder": "Введите пароль"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control py-4", "placeholder": "Подтвердите пароль"}))
    recaptcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY, private_key=settings.RECAPTCHA_PRIVATE_KEY, label="ReCAPTCHA"
    )

    def save(self, commit=True):
        user = super().save(commit=True)
        send_email_verification.delay(user.id)
        return user


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control py-4"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control py-4"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "custom-file-input"}), required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control py-4", "readonly": True}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"class": "form-control py-4", "readonly": True}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control py-4"}))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "image", "username", "email", "phone")


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Эл. почта",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "class": "form-control", "placeholder": "name@example.com"}),
    )
    recaptcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY, private_key=settings.RECAPTCHA_PRIVATE_KEY, label="ReCAPTCHA"
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control", "placeholder": "Введите пароль"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control", "placeholder": "Подтвердите пароль"}),
    )
