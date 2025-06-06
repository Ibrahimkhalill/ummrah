# Generated by Django 5.1.6 on 2025-03-22 13:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_remove_notification_visible_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='firebasetoken',
            name='token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='firebasetoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]
