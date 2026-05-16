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
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from apps.booking.models import Appointment

from .forms import ProfileUpdateForm, SignUpForm, StyledAuthenticationForm, UserUpdateForm


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
    if request.method == "POST" and "update_profile" in request.POST:
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Профиль успешно обновлен.")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    appointments = list(Appointment.objects.filter(user=request.user).select_related("service", "master"))
    
    upcoming = []
    history = []
    
    for app in appointments:
        if app.status in [Appointment.Status.NEW, Appointment.Status.CONFIRMED] and app.is_past:
            app.status = Appointment.Status.COMPLETED
            app.save(update_fields=["status"])
            
        if app.status in [Appointment.Status.CANCELED, Appointment.Status.COMPLETED]:
            history.append(app)
        else:
            upcoming.append(app)
            
    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "upcoming_appointments": upcoming,
            "history_appointments": history,
        },
    )
