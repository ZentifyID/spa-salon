from django.contrib.auth import get_user_model
from django.db import models

from apps.masters.models import Master
from apps.services.models import Service

User = get_user_model()


class Appointment(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        CONFIRMED = "confirmed", "Подтверждена"
        CANCELED = "canceled", "Отменена"

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    master = models.ForeignKey(
        Master,
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
    )
    appointment_at = models.DateTimeField(verbose_name="Дата и время")
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appointment_at"]

    def __str__(self) -> str:
        master_name = self.master.full_name if self.master else "Без мастера"
        return f"{self.full_name} - {self.service.name} ({master_name})"
