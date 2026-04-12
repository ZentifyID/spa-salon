from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("masters", "0002_masterschedule_masterdayoff"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(verbose_name="Оценка")),
                ("text", models.TextField(verbose_name="Текст отзыва")),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "На модерации"), ("approved", "Одобрен"), ("rejected", "Отклонен")],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("moderated_at", models.DateTimeField(blank=True, null=True)),
                (
                    "master",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="masters.master"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "verbose_name": "Отзыв",
                "verbose_name_plural": "Отзывы",
                "ordering": ["-created_at"],
                "unique_together": {("master", "user")},
            },
        ),
    ]
