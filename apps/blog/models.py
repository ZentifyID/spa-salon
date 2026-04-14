from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=180, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    cover_image = models.ImageField(
        upload_to="blog/covers/",
        blank=True,
        null=True,
        verbose_name="Обложка",
    )
    summary = models.TextField(max_length=320, verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Текст статьи")
    is_published = models.BooleanField(default=True, verbose_name="Опубликована")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})
