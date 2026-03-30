from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from apps.booking.models import Appointment

from .forms import SignUpForm, StyledAuthenticationForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Аккаунт создан. Добро пожаловать!")
            return redirect("accounts:profile")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile(request):
    appointments = Appointment.objects.filter(user=request.user).select_related("service")
    upcoming = appointments.exclude(status=Appointment.Status.CANCELED)
    history = appointments.filter(status=Appointment.Status.CANCELED)
    return render(
        request,
        "accounts/profile.html",
        {
            "upcoming_appointments": upcoming,
            "history_appointments": history,
        },
    )
