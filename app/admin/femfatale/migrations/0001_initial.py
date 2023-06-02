# Generated by Django 4.2.1 on 2023-06-01 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Назва')),
                ('category', models.CharField(max_length=20, verbose_name='Категорія')),
                ('address', models.CharField(max_length=500, verbose_name='Адреса')),
                ('cashback', models.CharField(max_length=50, null=True, verbose_name='Кешбек')),
                ('phone', models.CharField(max_length=12, null=True, verbose_name='Телефон')),
                ('city', models.CharField(default='Київ', max_length=20, null=True, verbose_name='Місто')),
                ('description', models.CharField(max_length=1000, null=True, verbose_name='Додаткова інформаці')),
            ],
            options={
                'verbose_name': 'Партнер',
                'verbose_name_plural': 'Партнери',
                'db_table': 'partners',
            },
        ),
    ]
