# Generated by Django 5.1.6 on 2025-03-11 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentications', '0010_guideprofile_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guideprofile',
            name='joined_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
