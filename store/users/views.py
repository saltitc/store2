from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import (LoginView, PasswordResetConfirmView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from common.views import TitleMixin

from .forms import (UserLoginForm, UserPasswordResetForm, UserProfileForm,
                    UserRegistrationForm, UserSetPasswordForm)
from .models import EmailVerification

User = get_user_model()


class UserLoginView(TitleMixin, LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm
    title = "Авторизация"


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:signin")
    success_message = "Вы успешно зарегистрированы!"
    title = "Регистрация"


class UserProfileView(TitleMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    title = "Профиль"


class EditUserProfileView(TitleMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/edit_profile.html"
    title = "Редактирование профиля"

    def dispatch(self, *args, **kwargs):
        if self.request.user != self.get_object():
            return redirect("users:profile", pk=self.request.user.id)
        return super(EditUserProfileView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("users:profile", args=(self.object.id,))


class EmailVerificationView(TitleMixin, TemplateView):
    title = "Подтверждение эл. почты"
    template_name = "users/email_verification.html"

    def get(self, request, *args, **kwargs):
        code = kwargs["code"]
        user = User.objects.get(email=kwargs["email"])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired() and not user.is_verified_email:
            user.is_verified_email = True
            user.save()
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse("products:index"))


class UserPasswordResetView(PasswordResetView):
    email_template_name = "users/password/reset_email.html"
    html_email_template_name = "users/password/reset_email.html"
    template_name = "users/password/reset.html"
    subject_template_name = "users/password/reset_subject.txt"
    form_class = UserPasswordResetForm
    title = "Сброс пароля"
    success_url = reverse_lazy("users:signin")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(self.request, "Аккаунта с данной эл. почтой не существует")
            form.add_error("email", "Аккаунта с данной эл. почтой не существует")
            return self.form_invalid(form)

        messages.success(self.request, "Письмо с инструкциями по сбросу пароля отправлено на вашу почту.")
        return super().form_valid(form)


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "users/password/reset_confirm.html"
    success_url = reverse_lazy("users:signin")
    form_class = UserSetPasswordForm
    title = "Создание нового пароля"

    def form_valid(self, form):
        messages.success(self.request, "Вы успешно сменили пароль! Теперь вы можете войти в ваш аккаунт с новым паролем.")
        return super().form_valid(form)
