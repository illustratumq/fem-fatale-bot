from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.
from django.forms import Textarea, ModelForm

from app.config import Config
from telebot import TeleBot

from app.keyboards import Buttons


class TimeBaseModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')


class Media(TimeBaseModel):

    class Meta:
        db_table = 'medias'
        verbose_name = 'медіа'
        verbose_name_plural = 'медіа'

    ContentTypeEnum = (
        ('VIDEO', 'Відео'),
        ('PHOTO', 'Фото')
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, null=True, blank=True, verbose_name='Назва медіа даних')
    files = ArrayField(ArrayField(models.CharField(blank=True)), verbose_name='Телеграм ID файлів', editable=False)
    content_type = models.CharField(choices=ContentTypeEnum, verbose_name='Тип файлів', editable=False)

    def __str__(self):
        return self.name


class Article(TimeBaseModel):

    class Meta:
        db_table = 'articles'
        verbose_name = 'новина'
        verbose_name_plural = 'новини'

    ArticleStatusEnum = (
        ('ACTIVE', 'Опублікована'),
        ('HIDE', 'Прихована')
    )

    id = models.BigAutoField(primary_key=True)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, verbose_name='Медіа файли', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Заголовок')
    description = models.CharField(max_length=1060, null=False, verbose_name='Основний текст', blank=True)
    status = models.CharField(choices=ArticleStatusEnum, default='HIDE', null=False, verbose_name='Статус')

    def __str__(self):
        return f'Новина №{self.id}'


class Partner(TimeBaseModel):

    class Meta:
        db_table = 'partners'
        verbose_name = 'партнер'
        verbose_name_plural = 'партнери'

    PARTNER_CATEGORIES = (
        ('Ресторани', 'Ресторани'),
        ('Масажні салони', 'Масажні салони'),
        ('Spa', 'Spa'),
        ('Магазини', 'Магазини'),
        ('Казино', 'Казино'),
        ('Караоке', 'Караоке'),
        ('Готелі', 'Готелі'),
        ('Салони краси', 'Салони краси'),
        ('Інше', 'Інше')
    )

    id = models.BigAutoField(primary_key=True)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, verbose_name='Медіа пакунок', null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='Назва закладу', null=False)
    category = models.CharField(max_length=20, verbose_name='Категорія', null=False)
    address = models.CharField(max_length=500, verbose_name='Адреса', null=False)
    cashback = models.CharField(max_length=50, verbose_name='Кешбек', null=True)
    phone = models.CharField(max_length=12, verbose_name='Телефон', null=True, blank=True)
    city = models.CharField(max_length=20, verbose_name='Місто', null=False, default='Київ')
    description = models.CharField(max_length=1000, verbose_name='Додаткова інформація', null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True, verbose_name='Приоритетність')

    def __str__(self):
        return f'{self.name} ({self.category}'


class User(TimeBaseModel):

    class Meta:
        db_table = 'users'
        verbose_name = 'клієнт'
        verbose_name_plural = 'клієнти'

    UserStatusEnum = (
        ('ACTIVE', 'Активний'),
        ('INACTIVE', 'Не активний'),
        ('UNAUTHORIZED', 'Не авторизований')
    )

    UserRoleEnum = (
        ('ADMIN', 'Адмін'),
        ('USER', 'Клієнт'),
        ('MODERATOR', 'Модератор'),
        ('COMPETITION', 'Конкурент'),
        ('PARTNER', 'Партнер')
    )

    user_id = models.BigIntegerField(primary_key=True, verbose_name='Телеграм ID')
    full_name = models.CharField(max_length=255, null=False, verbose_name='Ім\'я')
    status = models.CharField(choices=UserStatusEnum, null=False, default='UNAUTHORIZED', verbose_name='Статус')
    role = models.CharField(choices=UserRoleEnum, null=False, default='USER', verbose_name='Роль')
    phone = models.CharField(max_length=12, null=True, blank=True, verbose_name='Телефон')
    card = models.CharField(max_length=10, null=True, blank=True, verbose_name='Карта клієнта', unique=True)
    bankcard = models.CharField(max_length=16, null=True, blank=True, verbose_name='Банківська карта')
    balance = models.BigIntegerField(default=0, verbose_name='Баланс, грн', help_text='*Рахується автоматично')
    info = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Коментар для адміністраторів')

    def __str__(self):
        return f'{self.full_name} ({self.card})'


class Payout(TimeBaseModel):

    class Meta:
        db_table = 'payouts'
        verbose_name = 'платіж'
        verbose_name_plural = 'платежі'

    PayoutTypeEnum = (
        ('MINUS', 'Списання'),
        ('PLUS', 'Нарахування')
    )

    PayoutTagEnum = (
        ('default', 'Початковий баланс'),
        ('edited', 'Створений адміном платіж')
    )

    id = models.BigAutoField(primary_key=True)
    payout_date = models.DateTimeField(verbose_name='Дата отримання чеку', default=datetime.now())
    media = models.ForeignKey(Media,  on_delete=models.SET_NULL, verbose_name='Фото чеку', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Клієнт', null=False)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, verbose_name='Заклад', null=True, blank=True)

    # PRICE
    price = models.IntegerField(verbose_name='Чиста сума чеку, грн', help_text='Обов\'язкове поле')
    general_price = models.IntegerField(verbose_name='Загальний кешбек, грн', null=True, blank=True,
                                        help_text='*Рахується автоматично після зберігання')
    service_price = models.IntegerField(verbose_name='Наш кешбек, грн', null=True, blank=True,
                                        help_text='*Рахується автоматично після зберігання')
    user_price = models.IntegerField(verbose_name='Кешбек клієнта, грн', null=True, blank=True,
                                     help_text='*Рахується автоматично після зберігання')

    # PERCENT
    general_percent = models.IntegerField(verbose_name='Загальний кешбек',
                                          help_text='Загальний відсоток кешбеку, який нам платить заклад. '
                                                    'Обов\'язкове поле')
    service_percent = models.IntegerField(verbose_name='Наш прибуток',
                                          help_text='Відсоток кешбеку, який ми залишаємо собі. Обов\'язкове поле')
    user_percent = models.IntegerField(verbose_name='Кешбкек клієнта',
                                       help_text='Відсоток кешбеку, який отримає клієнт. Обов\'язкове поле')

    # OTHER//
    comment = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Коментар для клієнта',
                               help_text='Цей коментар побачить клієнт')
    description = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Коментар для адміністраторів')
    type = models.CharField(choices=PayoutTypeEnum, default='MINUS', null=False, verbose_name='Тип операції')
    tag = models.CharField(choices=PayoutTagEnum, verbose_name='Тип платежу', default='edited')

    def __str__(self):
        return f'{"-" if self.type == "MINUS" else "+"} {self.price} грн. для ' \
               f'{self.user.full_name}'

    def save(self, *args, **kwargs):
        self.general_price = round(self.general_percent / 100 * self.price)
        self.service_price = round(self.service_percent / 100 * self.price)
        user_price = round(self.user_percent / 100 * self.price)
        self.user_price = user_price
        if not Payout.objects.filter(id=self.id):
            config = Config.from_env()
            bot = TeleBot(config.bot.token)
            action = 'Тобі було нараховано' if self.type == 'PLUS' else 'З тебе було списано'
            text = (
                f'🔔 {action} {self.user_price} балів.\n\n'
                f'Перейдіть в розділ <b>{Buttons.menu.balance}</b>, '
                f'щоб переглянути повну інформацію'
            )
            try:
                bot.send_message(self.user.user_id, text, parse_mode='HTML')
            except:
                pass
        save = super(Payout, self).save(*args, **kwargs)
        balance = 0
        for payout in Payout.objects.filter(user_id=self.user.user_id):
            if payout.type == 'MINUS':
                balance -= payout.user_price
            else:
                balance += payout.user_price
        self.user.balance = balance
        super(User, self.user).save()
        return save

    def delete(self, *args, **kwargs):
        config = Config.from_env()
        bot = TeleBot(config.bot.token)
        text = (
            f'🔔 Ваш платіж {"+" if self.type == "PLUS" else "-"} {self.user_price} грн. був видалений адміністратором. '
            f'Для уточення напишіть нам, в розділі <b>{Buttons.menu.help}</b>'
        )
        try:
            bot.send_message(self.user.user_id, text, parse_mode='HTML')
        except:
            pass
        delete = super(Payout, self).delete(*args, **kwargs)
        balance = 0
        for payout in Payout.objects.filter(user_id=self.user.user_id):
            if payout.type == 'MINUS':
                balance -= payout.user_price
            else:
                balance += payout.user_price
        self.user.balance = balance
        super(User, self.user).save()
        return delete


class BaseForm(ModelForm):
    class Meta:
        fields = '__all__'

        widgets = {
            'info': Textarea(attrs={'cols': 100, 'rows': 5}),
            'description': Textarea(attrs={'cols': 100, 'rows': 5}),
            'files': Textarea(attrs={'cols': 100, 'rows': 5}),
            'address': Textarea(attrs={'cols': 100, 'rows': 3})
        }

