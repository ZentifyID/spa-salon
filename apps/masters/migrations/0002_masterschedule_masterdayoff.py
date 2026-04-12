import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("masters", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MasterDayOff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Дата")),
                ("reason", models.CharField(blank=True, max_length=200, verbose_name="Причина")),
                (
                    "master",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="days_off", to="masters.master"),
                ),
            ],
            options={
                "verbose_name": "Выходной мастера",
                "verbose_name_plural": "Выходные мастеров",
                "ordering": ["-date"],
                "unique_together": {("master", "date")},
            },
        ),
        migrations.CreateModel(
            name="MasterSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "weekday",
                    models.IntegerField(
                        choices=[
                            (0, "Понедельник"),
                            (1, "Вторник"),
                            (2, "Среда"),
                            (3, "Четверг"),
                            (4, "Пятница"),
                            (5, "Суббота"),
                            (6, "Воскресенье"),
                        ],
                        verbose_name="День недели",
                    ),
                ),
                ("work_start", models.TimeField(verbose_name="Начало работы")),
                ("work_end", models.TimeField(verbose_name="Окончание работы")),
                ("is_working_day", models.BooleanField(default=True, verbose_name="Рабочий день")),
                (
                    "master",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="schedules", to="masters.master"),
                ),
            ],
            options={
                "verbose_name": "Расписание мастера",
                "verbose_name_plural": "Расписания мастеров",
                "ordering": ["master", "weekday"],
                "unique_together": {("master", "weekday")},
            },
        ),
    ]
