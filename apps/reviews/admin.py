from django.contrib import admin
from django.utils import timezone

from .models import Review


@admin.action(description="Одобрить выбранные отзывы")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(status=Review.Status.APPROVED, moderated_at=timezone.now())


@admin.action(description="Отклонить выбранные отзывы")
def reject_reviews(modeladmin, request, queryset):
    queryset.update(status=Review.Status.REJECTED, moderated_at=timezone.now())


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("master", "user", "rating", "status", "created_at", "moderated_at")
    list_filter = ("status", "rating", "master")
    search_fields = ("master__full_name", "user__username", "text")
    actions = (approve_reviews, reject_reviews)
    list_editable = ("status",)

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            obj.moderated_at = timezone.now()
        super().save_model(request, obj, form, change)
