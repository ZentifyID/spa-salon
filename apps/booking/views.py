from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import AppointmentForm


def create_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка успешно отправлена. Мы свяжемся с вами для подтверждения.")
            return redirect("booking:create")
    else:
        form = AppointmentForm()

    return render(request, "booking/create_appointment.html", {"form": form})
