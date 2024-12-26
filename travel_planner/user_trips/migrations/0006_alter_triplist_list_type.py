# Generated by Django 5.1.4 on 2024-12-26 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_trips', '0005_listitem_remove_mytrip_chosen_hotel_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triplist',
            name='list_type',
            field=models.CharField(choices=[('attractions', 'Attractions'), ('restaurants', 'Restaurants'), ('notes', 'Notes')], max_length=20),
        ),
    ]
