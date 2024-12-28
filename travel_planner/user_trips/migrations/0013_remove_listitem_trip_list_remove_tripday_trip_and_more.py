# Generated by Django 5.1.4 on 2024-12-28 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_trips', '0012_mytrip_attractions_mytrip_restaurants'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listitem',
            name='trip_list',
        ),
        migrations.RemoveField(
            model_name='tripday',
            name='trip',
        ),
        migrations.RemoveField(
            model_name='triplist',
            name='trip',
        ),
        migrations.DeleteModel(
            name='DayActivity',
        ),
        migrations.DeleteModel(
            name='ListItem',
        ),
        migrations.DeleteModel(
            name='TripDay',
        ),
        migrations.DeleteModel(
            name='TripList',
        ),
    ]