# Generated by Django 4.2.1 on 2023-06-01 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('femfatale', '0002_alter_partner_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='description',
            field=models.CharField(max_length=1000, null=True, verbose_name='Додаткова інформація'),
        ),
    ]
