# Generated by Django 4.2.15 on 2024-10-11 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("network", "0002_alter_follower_list_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="edited",
            field=models.BooleanField(default=False),
        ),
    ]
