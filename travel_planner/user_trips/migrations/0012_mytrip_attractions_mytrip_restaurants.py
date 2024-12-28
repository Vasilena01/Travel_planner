# Generated by Django 5.1.4 on 2024-12-27 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_trips', '0011_remove_mytrip_attractions_remove_mytrip_restaurants_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mytrip',
            name='attractions',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='mytrip',
            name='restaurants',
            field=models.JSONField(default=list),
        ),
    ]