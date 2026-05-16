from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from apps.masters.models import Master
from apps.services.models import Service
from apps.promotions.models import PromoCode

from .forms import AppointmentForm
from .models import Appointment
from .scheduling import SLOT_STEP_MINUTES, get_available_slots, validate_master_slot


def create_appointment(request):
    initial = {}
    if service_id := request.GET.get("service"):
        initial["service"] = service_id

    if request.user.is_authenticated:
        initial.update(
            {
                "full_name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone": getattr(request.user.profile, "phone", ""),
            }
        )

    if request.method == "POST":
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            if request.user.is_authenticated:
                appointment.user = request.user

            with transaction.atomic():
                # Lock relevant rows on databases that support row-level locking.
                Master.objects.select_for_update().filter(pk=appointment.master_id).exists()
                Appointment.objects.select_for_update().filter(
                    master_id=appointment.master_id,
                    appointment_at__date=appointment.appointment_at.date(),
                    status__in=[Appointment.Status.NEW, Appointment.Status.CONFIRMED],
                ).exists()

                is_valid_slot, message = validate_master_slot(
                    appointment.master,
                    appointment.service,
                    appointment.appointment_at,
                )
                if not is_valid_slot:
                    form.add_error("appointment_at", message)
                else:
                    # Calculate total price
                    total = appointment.service.price
                    if appointment.promo_code:
                        promo = PromoCode.objects.filter(code__iexact=appointment.promo_code).first()
                        if promo and promo.is_valid():
                            if promo.discount_type == PromoCode.DiscountType.PERCENT:
                                total -= (total * promo.discount_value) / 100
                            else:
                                total -= promo.discount_value
                    
                    appointment.total_price = max(total, 0)
                    appointment.save()
                    
                    messages.success(request, "Запись создана. Пожалуйста, оплатите заказ.")
                    return redirect("booking:checkout", pk=appointment.pk)
    else:
        form = AppointmentForm(initial=initial, user=request.user)

    return render(request, "booking/create_appointment.html", {"form": form})


def masters_by_service(request):
    service_id = request.GET.get("service_id")
    masters = []
    if service_id:
        masters = list(
            Master.objects.filter(is_active=True, services__id=service_id)
            .distinct()
            .values("id", "full_name")
        )
    return JsonResponse({"masters": masters})


def slots_by_master(request):
    service_id = request.GET.get("service_id")
    master_id = request.GET.get("master_id")
    date_raw = request.GET.get("date")

    if not service_id or not master_id or not date_raw:
        return JsonResponse({"slots": []})

    date_value = parse_date(date_raw)
    if not date_value:
        return JsonResponse({"slots": []})

    master = Master.objects.filter(pk=master_id, is_active=True).first()
    service = Service.objects.filter(pk=service_id, is_active=True).first()
    if not master or not service or not master.services.filter(pk=service.pk).exists():
        return JsonResponse({"slots": []})

    slots = get_available_slots(master, service, date_value)
    slots_payload = [slot.strftime("%H:%M") for slot in slots]
    return JsonResponse({"slots": slots_payload, "slot_step_minutes": SLOT_STEP_MINUTES})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELED
        appointment.save(update_fields=["status"])
        messages.success(request, "Запись отменена.")
    return redirect("accounts:profile")


def checkout(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.is_paid:
        return redirect("accounts:profile" if request.user.is_authenticated else "core:home")
        
    return render(request, "booking/checkout.html", {"appointment": appointment})


def confirm_payment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.is_paid = True
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=["is_paid", "status"])
        messages.success(request, "Оплата прошла успешно! Ждем вас в нашем салоне.")
        
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    return redirect("core:home")
