# Generated by Django 4.0 on 2025-01-10 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_alter_stockholding_price_buy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(default='Person Name', max_length=50),
        ),
    ]
