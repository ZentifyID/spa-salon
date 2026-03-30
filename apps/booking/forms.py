from django import forms
from django.utils import timezone

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"field-control {css_class}".strip()
        self.fields["comment"].widget.attrs["rows"] = 4

    def clean_appointment_at(self):
        appointment_at = self.cleaned_data["appointment_at"]
        if appointment_at <= timezone.now():
            raise forms.ValidationError("Выберите дату и время в будущем.")
        return appointment_at
