# Generated by Django 4.2.6 on 2024-10-25 01:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_payment_cost_budget'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='peyment',
        ),
    ]
