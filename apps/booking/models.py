from django.db import models

from apps.services.models import Service


class Appointment(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        CONFIRMED = "confirmed", "Подтверждена"
        CANCELED = "canceled", "Отменена"

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    appointment_at = models.DateTimeField(verbose_name="Дата и время")
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appointment_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.service.name}"
