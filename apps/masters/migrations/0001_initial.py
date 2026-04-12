from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Master",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120, verbose_name="ФИО")),
                ("bio", models.TextField(blank=True, verbose_name="О специалисте")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("services", models.ManyToManyField(related_name="masters", to="services.service", verbose_name="Услуги")),
            ],
            options={
                "verbose_name": "Мастер",
                "verbose_name_plural": "Мастера",
                "ordering": ["full_name"],
            },
        ),
    ]
