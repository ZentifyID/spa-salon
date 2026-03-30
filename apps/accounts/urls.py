from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import UserLoginView, profile, signup

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile, name="profile"),
]
