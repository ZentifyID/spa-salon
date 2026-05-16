from django import forms
from django.utils import timezone

from apps.masters.models import Master
from apps.services.models import Service
from apps.promotions.models import PromoCode

from .models import Appointment
from .scheduling import validate_master_slot


class AppointmentForm(forms.ModelForm):
    appointment_at = forms.DateTimeField(
        label="Желаемая дата и время",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Appointment
        fields = [
            "full_name",
            "phone",
            "email",
            "service",
            "master",
            "appointment_at",
            "promo_code",
            "comment",
        ]
        labels = {
            "full_name": "Имя",
            "phone": "Телефон",
            "email": "Email",
            "service": "Услуга",
            "master": "Мастер",
            "promo_code": "Промокод",
            "comment": "Комментарий",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

        selected_service_id = self.data.get("service") or self.initial.get("service")
        if self.instance.pk and not selected_service_id:
            selected_service_id = self.instance.service_id

        available_masters = Master.objects.filter(is_active=True)
        if selected_service_id:
            available_masters = available_masters.filter(services__id=selected_service_id).distinct()
        else:
            available_masters = available_masters.none()

        self.fields["master"].queryset = available_masters
        self.fields["master"].help_text = "Сначала выберите услугу, затем мастера."
        self.fields["master"].required = True

        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"field-control {css_class}".strip()
        self.fields["comment"].widget.attrs["rows"] = 4

    def clean_promo_code(self):
        code = self.cleaned_data.get("promo_code")
        if not code:
            return ""
        
        promo = PromoCode.objects.filter(code__iexact=code).first()
        if not promo:
            raise forms.ValidationError("Неверный промокод.")
        
        if not promo.is_valid():
            raise forms.ValidationError("Срок действия этого промокода истек или он неактивен.")

        # Check for one-time usage per user
        if self.user and self.user.is_authenticated:
            # Check if user already has a non-canceled appointment with this promo code
            already_used = Appointment.objects.filter(
                user=self.user,
                promo_code__iexact=code,
            ).exclude(status=Appointment.Status.CANCELED).exists()
            
            if already_used:
                raise forms.ValidationError("Вы уже использовали этот промокод.")
            
        return promo.code

    def clean_appointment_at(self):
        appointment_at = self.cleaned_data["appointment_at"]
        if timezone.is_naive(appointment_at):
            appointment_at = timezone.make_aware(appointment_at, timezone.get_current_timezone())
        if appointment_at <= timezone.now():
            raise forms.ValidationError("Выберите дату и время в будущем.")
        return appointment_at

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        master = cleaned_data.get("master")
        appointment_at = cleaned_data.get("appointment_at")

        if not service or not master or not appointment_at:
            return cleaned_data

        if not service.is_active:
            self.add_error("service", "Выбранная услуга недоступна для записи.")
            return cleaned_data

        if not master.services.filter(pk=service.pk).exists():
            self.add_error("master", "Этот мастер не выполняет выбранную услугу.")
            return cleaned_data

        is_valid_slot, message = validate_master_slot(
            master,
            service,
            appointment_at,
            exclude_appointment_id=self.instance.pk,
        )
        if not is_valid_slot:
            self.add_error("appointment_at", message)

        return cleaned_data
