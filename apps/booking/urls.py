from django.urls import path

from .views import create_appointment

app_name = "booking"

urlpatterns = [
    path("", create_appointment, name="create"),
]
