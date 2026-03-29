import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("appointment_at", models.DateTimeField(verbose_name="Дата и время")),
                ("comment", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "Новая"), ("confirmed", "Подтверждена"), ("canceled", "Отменена")],
                        default="new",
                        max_length=12,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "service",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="services.service"),
                ),
            ],
            options={"ordering": ["-appointment_at"]},
        ),
    ]
