# Generated by Django 4.2.15 on 2024-10-07 06:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("network", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="follower_list",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                unique=True,
            ),
        ),
    ]
