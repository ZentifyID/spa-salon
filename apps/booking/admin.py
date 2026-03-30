from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "service", "appointment_at", "status", "user")
    list_filter = ("status", "service")
    search_fields = ("full_name", "phone", "email")
