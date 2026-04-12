from django.urls import path

from .views import master_detail, master_list

app_name = "masters"

urlpatterns = [
    path("", master_list, name="list"),
    path("<int:pk>/", master_detail, name="detail"),
]
