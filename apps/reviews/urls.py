from django.urls import path

from .views import create_or_update_review

app_name = "reviews"

urlpatterns = [
    path("masters/<int:master_id>/", create_or_update_review, name="create_or_update"),
]
