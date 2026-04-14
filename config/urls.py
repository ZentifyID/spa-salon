"""
URL configuration for config project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("services/", include("apps.services.urls")),
    path("masters/", include("apps.masters.urls")),
    path("booking/", include("apps.booking.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("blog/", include("apps.blog.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
