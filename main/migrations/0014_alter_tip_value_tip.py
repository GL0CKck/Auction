# Generated by Django 3.2.5 on 2021-08-07 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_tip_id_tip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tip',
            name='value_tip',
            field=models.IntegerField(default=0, verbose_name='Ваша ставка'),
        ),
    ]