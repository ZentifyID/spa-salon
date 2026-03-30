from django.shortcuts import render

from apps.services.models import Service


def home(request):
    featured_services = Service.objects.filter(is_active=True)[:3]
    context = {
        "featured_services": featured_services,
        "services_count": Service.objects.filter(is_active=True).count(),
    }
    return render(request, "core/home.html", context)
