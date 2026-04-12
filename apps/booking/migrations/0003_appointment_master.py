import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("masters", "0001_initial"),
        ("booking", "0002_appointment_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="master",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="appointments",
                to="masters.master",
            ),
        ),
    ]
