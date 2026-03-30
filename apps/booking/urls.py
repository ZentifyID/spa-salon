from django.urls import path

from .views import cancel_appointment, create_appointment

app_name = "booking"

urlpatterns = [
    path("", create_appointment, name="create"),
    path("<int:pk>/cancel/", cancel_appointment, name="cancel"),
]
