# Generated by Django 4.2.1 on 2023-06-01 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('femfatale', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
