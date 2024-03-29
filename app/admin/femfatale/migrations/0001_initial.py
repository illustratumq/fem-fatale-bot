# Generated by Django 4.2.1 on 2023-06-03 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(blank=True, max_length=200, null=True, verbose_name='Фото')),
                ('name', models.CharField(max_length=100, verbose_name='Назва')),
                ('category', models.CharField(choices=[('Ресторани', 'Ресторани'), ('Масажні салони', 'Масажні салони'), ('Spa', 'Spa'), ('Магазини', 'Магазини'), ('Казино', 'Казино'), ('Караоке', 'Караоке'), ('Готелі', 'Готелі'), ('Інше', 'Інше')], max_length=20, verbose_name='Категорія')),
                ('address', models.CharField(max_length=500, verbose_name='Адреса')),
                ('cashback', models.CharField(max_length=50, null=True, verbose_name='Кешбек')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='Телефон')),
                ('city', models.CharField(default='Київ', max_length=20, verbose_name='Місто')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Додаткова інформація')),
            ],
            options={
                'verbose_name': 'Партнер',
                'verbose_name_plural': 'Партнери',
                'db_table': 'partners',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')),
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='Телеграм ID')),
                ('full_name', models.CharField(max_length=255, verbose_name="Ім'я")),
                ('status', models.CharField(choices=[('ACTIVE', 'Активний'), ('INACTIVE', 'Не активний'), ('UNAUTHORIZED', 'Не авторизований')], default='UNAUTHORIZED', verbose_name='Статус')),
                ('role', models.CharField(choices=[('ADMIN', 'Адмін'), ('USER', 'Клієнт'), ('MODERATOR', 'Модератор'), ('COMPETITION', 'Конкурент'), ('PARTNER', 'Партнер')], default='USER', verbose_name='Роль')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='Телефон')),
                ('card', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Карточка')),
                ('bankcard', models.CharField(blank=True, max_length=16, null=True, verbose_name='Банківська карта')),
                ('balance', models.BigIntegerField(default=0, verbose_name='Баланс')),
                ('info', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Додаткова інформація')),
            ],
            options={
                'verbose_name': 'Клієнт',
                'verbose_name_plural': 'Клієнти',
                'db_table': 'users',
            },
        ),
    ]
