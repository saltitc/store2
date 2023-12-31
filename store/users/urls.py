from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (EditUserProfileView, EmailVerificationView, UserLoginView,
                    UserPasswordResetConfirmView, UserPasswordResetView,
                    UserProfileView, UserRegistrationView)

app_name = "users"

urlpatterns = [
    path("signin/", UserLoginView.as_view(), name="signin"),
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("profile/<int:pk>/", login_required(UserProfileView.as_view()), name="profile"),
    path("profile/<int:pk>/edit/", login_required(EditUserProfileView.as_view()), name="profile_edit"),
    path("signout/", LogoutView.as_view(), name="signout"),
    path("verify/<str:email>/<uuid:code>", EmailVerificationView.as_view(), name="email_verification"),
    path("password_reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("reset/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
