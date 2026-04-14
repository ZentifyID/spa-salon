from django.urls import path

from .views import article_detail, article_list

app_name = "blog"

urlpatterns = [
    path("", article_list, name="list"),
    path("<slug:slug>/", article_detail, name="detail"),
]
