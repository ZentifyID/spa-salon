from django import forms

from .models import Appointment


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
            "appointment_at",
            "comment",
        ]
        labels = {
            "full_name": "Имя",
            "phone": "Телефон",
            "email": "Email",
            "service": "Услуга",
            "comment": "Комментарий",
        }
