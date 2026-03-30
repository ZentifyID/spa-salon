from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AppointmentForm
from .models import Appointment


def create_appointment(request):
    initial = {}
    if service_id := request.GET.get("service"):
        initial["service"] = service_id

    if request.user.is_authenticated:
        initial.update(
            {
                "full_name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
            }
        )

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if request.user.is_authenticated:
                appointment.user = request.user
            appointment.save()
            messages.success(request, "Запись создана. Мы свяжемся с вами для подтверждения.")
            if request.user.is_authenticated:
                return redirect("accounts:profile")
            return redirect("booking:create")
    else:
        form = AppointmentForm(initial=initial)

    return render(request, "booking/create_appointment.html", {"form": form})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELED
        appointment.save(update_fields=["status"])
        messages.success(request, "Запись отменена.")
    return redirect("accounts:profile")
