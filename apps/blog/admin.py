from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "has_cover")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Обложка")
    def has_cover(self, obj):
        return bool(obj.cover_image)
