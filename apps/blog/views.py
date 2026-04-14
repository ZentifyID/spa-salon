from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Article


def article_list(request):
    articles = Article.objects.filter(is_published=True, published_at__lte=timezone.now())
    return render(request, "blog/article_list.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
        published_at__lte=timezone.now(),
    )
    return render(request, "blog/article_detail.html", {"article": article})
