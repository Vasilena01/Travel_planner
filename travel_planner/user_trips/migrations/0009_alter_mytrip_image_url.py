# Generated by Django 5.1.4 on 2024-12-27 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_trips', '0008_mytrip_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mytrip',
            name='image_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]