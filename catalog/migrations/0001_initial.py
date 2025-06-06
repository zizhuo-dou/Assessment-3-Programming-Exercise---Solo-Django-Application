# Generated by Django 3.2 on 2025-05-09 03:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Star',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('constellation', models.CharField(max_length=100)),
                ('magnitude', models.FloatField()),
                ('ra', models.FloatField(help_text='Right Ascension')),
                ('dec', models.FloatField(help_text='Declination')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_given', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, default=19.99, max_digits=6)),
                ('date_ordered', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'In Cart'), ('paid', 'Paid, Awaiting Confirmation'), ('confirmed', 'Confirmed & Named')], default='pending', max_length=20)),
                ('star', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.star')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
