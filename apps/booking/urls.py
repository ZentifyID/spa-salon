from django.urls import path

from .views import (
    cancel_appointment,
    checkout,
    confirm_payment,
    create_appointment,
    masters_by_service,
    slots_by_master,
)

app_name = "booking"

urlpatterns = [
    path("", create_appointment, name="create"),
    path("masters/", masters_by_service, name="masters_by_service"),
    path("slots/", slots_by_master, name="slots_by_master"),
    path("<int:pk>/checkout/", checkout, name="checkout"),
    path("<int:pk>/checkout/confirm/", confirm_payment, name="confirm_payment"),
    path("<int:pk>/cancel/", cancel_appointment, name="cancel"),
]
