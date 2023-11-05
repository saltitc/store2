from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
    EmailVerificationView,
)

app_name = "users"

urlpatterns = [
    path("signin/", UserLoginView.as_view(), name="signin"),
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("profile/<int:pk>/", login_required(UserProfileView.as_view()), name="profile"),
    path("signout/", LogoutView.as_view(), name="signout"),
    path("verify/<str:email>/<uuid:code>", EmailVerificationView.as_view(), name="email_verification"),
]
