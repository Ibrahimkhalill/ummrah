# Generated by Django 5.1.6 on 2025-03-11 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_helpsupport_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helpsupport',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
