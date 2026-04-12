from django.db import models
from django.core.exceptions import ValidationError

from apps.services.models import Service


class Master(models.Model):
    full_name = models.CharField(max_length=120, verbose_name="ФИО")
    bio = models.TextField(blank=True, verbose_name="О специалисте")
    services = models.ManyToManyField(Service, related_name="masters", verbose_name="Услуги")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self) -> str:
        return self.full_name


class MasterSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Понедельник"
        TUESDAY = 1, "Вторник"
        WEDNESDAY = 2, "Среда"
        THURSDAY = 3, "Четверг"
        FRIDAY = 4, "Пятница"
        SATURDAY = 5, "Суббота"
        SUNDAY = 6, "Воскресенье"

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="schedules")
    weekday = models.IntegerField(choices=Weekday.choices, verbose_name="День недели")
    work_start = models.TimeField(verbose_name="Начало работы")
    work_end = models.TimeField(verbose_name="Окончание работы")
    is_working_day = models.BooleanField(default=True, verbose_name="Рабочий день")

    class Meta:
        unique_together = ("master", "weekday")
        ordering = ["master", "weekday"]
        verbose_name = "Расписание мастера"
        verbose_name_plural = "Расписания мастеров"

    def __str__(self) -> str:
        return f"{self.master.full_name} - {self.get_weekday_display()}"

    def clean(self):
        if self.work_end <= self.work_start:
            raise ValidationError("Время окончания должно быть позже времени начала.")


class MasterDayOff(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="days_off")
    date = models.DateField(verbose_name="Дата")
    reason = models.CharField(max_length=200, blank=True, verbose_name="Причина")

    class Meta:
        unique_together = ("master", "date")
        ordering = ["-date"]
        verbose_name = "Выходной мастера"
        verbose_name_plural = "Выходные мастеров"

    def __str__(self) -> str:
        return f"{self.master.full_name} - {self.date}"
