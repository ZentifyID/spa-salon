from django.shortcuts import render
from django.utils import timezone

from apps.blog.models import Article
from apps.reviews.models import Review
from apps.services.models import Service


def home(request):
    featured_services = Service.objects.filter(is_active=True)[:2]
    latest_articles = Article.objects.filter(
        is_published=True,
        published_at__lte=timezone.now(),
    )[:2]
    latest_reviews = (
        Review.objects.filter(status=Review.Status.APPROVED)
        .select_related("master", "user")[:3]
    )

    context = {
        "featured_services": featured_services,
        "latest_articles": latest_articles,
        "latest_reviews": latest_reviews,
        "services_count": Service.objects.filter(is_active=True).count(),
    }
    return render(request, "core/home.html", context)
