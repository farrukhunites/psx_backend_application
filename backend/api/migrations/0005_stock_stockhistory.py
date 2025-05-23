# Generated by Django 4.0 on 2025-01-07 05:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_dashboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('stock_symbol', models.CharField(max_length=10, unique=True)),
                ('stock_name', models.CharField(max_length=100)),
                ('sector', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('closing_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('high_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('low_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='api.stock')),
            ],
            options={
                'unique_together': {('stock', 'date')},
            },
        ),
    ]
