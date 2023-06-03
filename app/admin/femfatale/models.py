from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.
from django.forms import Textarea, ModelForm


class TimeBaseModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')


class Media(TimeBaseModel):

    class Meta:
        db_table = 'medias'
        verbose_name = 'Медіа'
        verbose_name_plural = 'Медіа'

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, null=True, blank=True, verbose_name='Назва медіа даних')
    files = ArrayField(ArrayField(models.CharField(blank=True)), verbose_name='Телеграм ID файлів')

    def __str__(self):
        return f'Медіа дані №{self.id}' + '' if not self.name else f' {self.name}'


class Article(TimeBaseModel):

    class Meta:
        db_table = 'articles'
        verbose_name = 'Новина'
        verbose_name_plural = 'Новини'

    ArticleStatusEnum = (
        ('ACTIVE', 'Опублікована'),
        ('HIDE', 'Прихована')
    )

    id = models.BigAutoField(primary_key=True)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, verbose_name='Медіа файли', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Заголовок')
    description = models.CharField(max_length=1060, null=False, verbose_name='Основний текст', blank=True)
    status = models.CharField(choices=ArticleStatusEnum, default='HIDE', null=False, verbose_name='Статус')


class Partner(TimeBaseModel):

    class Meta:
        db_table = 'partners'
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнери'

    PARTNER_CATEGORIES = (
        ('Ресторани', 'Ресторани'),
        ('Масажні салони', 'Масажні салони'),
        ('Spa', 'Spa'),
        ('Магазини', 'Магазини'),
        ('Казино', 'Казино'),
        ('Караоке', 'Караоке'),
        ('Готелі', 'Готелі'),
        ('Інше', 'Інше')
    )

    id = models.BigAutoField(primary_key=True)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, verbose_name='Медіа файли', null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='Назва', null=False)
    category = models.CharField(max_length=20, choices=PARTNER_CATEGORIES, verbose_name='Категорія', null=False)
    address = models.CharField(max_length=500, verbose_name='Адреса', null=False)
    cashback = models.CharField(max_length=50, verbose_name='Кешбек', null=True)
    phone = models.CharField(max_length=12, verbose_name='Телефон', null=True, blank=True)
    city = models.CharField(max_length=20, verbose_name='Місто', null=False, default='Київ')
    description = models.CharField(max_length=1000, verbose_name='Додаткова інформація', null=True, blank=True)

    def __str__(self):
        return f'№{self.id} {self.name} - {self.category}'


class User(TimeBaseModel):

    class Meta:
        db_table = 'users'
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    UNAUTHORIZED = 'UNAUTHORIZED'

    UserStatusEnum = (
        (ACTIVE, 'Активний'),
        (INACTIVE, 'Не активний'),
        (UNAUTHORIZED, 'Не авторизований')
    )

    ADMIN = 'ADMIN'
    USER = 'USER'
    MODERATOR = 'MODERATOR'
    COMPETITION = 'COMPETITION'
    PARTNER = 'PARTNER'

    UserRoleEnum = (
        (ADMIN, 'Адмін'),
        (USER, 'Клієнт'),
        (MODERATOR, 'Модератор'),
        (COMPETITION, 'Конкурент'),
        (PARTNER, 'Партнер')
    )

    user_id = models.BigIntegerField(primary_key=True, verbose_name='Телеграм ID')
    full_name = models.CharField(max_length=255, null=False, verbose_name='Ім\'я')
    status = models.CharField(choices=UserStatusEnum, null=False, default=UNAUTHORIZED, verbose_name='Статус')
    role = models.CharField(choices=UserRoleEnum, null=False, default=USER, verbose_name='Роль')
    phone = models.CharField(max_length=12, null=True, blank=True, verbose_name='Телефон')
    card = models.CharField(max_length=10, null=True, blank=True, verbose_name='Карточка', unique=True)
    bankcard = models.CharField(max_length=16, null=True, blank=True, verbose_name='Банківська карта')
    balance = models.BigIntegerField(default=0, verbose_name='Баланс')
    info = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Додаткова інформація')


class BaseForm(ModelForm):
    class Meta:
        fields = '__all__'

        widgets = {
            'info': Textarea(attrs={'cols': 100, 'rows': 5}),
            'description': Textarea(attrs={'cols': 100, 'rows': 5}),
            'files': Textarea(attrs={'cols': 100, 'rows': 5}),
            'address': Textarea(attrs={'cols': 100, 'rows': 3})
        }

