# Generated by Django 5.1.1 on 2024-10-01 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_merge_0004_restaurant_place_id_0004_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='place_id',
            field=models.CharField(default='default_value', max_length=255),
        ),
    ]
