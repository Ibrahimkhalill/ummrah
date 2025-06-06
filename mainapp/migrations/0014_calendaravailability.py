# Generated by Django 5.1.6 on 2025-03-18 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentications', '0011_alter_guideprofile_joined_date'),
        ('mainapp', '0013_rename_locations_transactions_services'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked')], default='available', max_length=10)),
                ('guide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar', to='authentications.guideprofile')),
            ],
        ),
    ]
