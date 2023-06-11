from django.contrib import admin
from .models import Partner, User, Media, Article, Payout, BaseForm


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('name', 'id', 'created_at')
    ordering = ['-created_at']
    search_fields = ('name', 'id')


@admin.action(description='Відкрити обрані новини')
def make_published(modeladmin, request, queryset):
    queryset.update(status='ACTIVE')


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('name', 'category', 'city', 'priority', 'updated_at')
    list_filter = ('city', 'category')
    search_fields = ('name__startswith', 'category__startswith')
    ordering = ['-updated_at', '-priority']
    autocomplete_fields = ('media', )

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'category', 'cashback')
        }),
        ('Партнерські дані', {
            'fields': ('city', 'address', 'phone'),
        }),
        ('Інше', {
            'fields': ('description', 'priority'),
        }),
    )


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('__str__', 'price', 'user', 'updated_at')
    list_filter = ('type', 'tag')
    search_fields = ("user_id__startswith",)
    ordering = ['-updated_at', '-tag']
    autocomplete_fields = ('user', 'media', 'partner')

    fieldsets = (
        ('Тип платежу', {
            'fields': ('tag', 'type')
        }),
        ('Призначення чеку', {
            'fields': ('user', 'partner', 'media', 'payout_date', 'comment')
        }),
        ('Кешбек та сума чеку', {
            'fields': ('price', 'general_price', 'service_price', 'user_price'),
        }),
        ('Розподіл відсотків', {
            'fields': ('general_percent', 'service_percent', 'user_percent'),
        }),
        ('Для адміністраторів', {
            'fields': ('description',),
        }),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('title', 'status', 'id', 'media_id', 'updated_at')
    list_filter = ('status',)
    search_fields = ("name__startswith",)
    ordering = ['-updated_at']
    actions = [make_published]
    autocomplete_fields = ('media',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('full_name', 'card', 'phone', 'balance', 'role', 'status', 'updated_at')
    list_filter = ('status', 'role')
    search_fields = ('card__startswith', 'full_name__startswith')
    ordering = ['-updated_at']

    fieldsets = (
        ('Персональна інформація про клієнта', {
            'fields': ('full_name', 'phone', 'bankcard')
        }),
        ('Сервісна інформація про клієнта', {
            'fields': ('card', 'balance', 'role', 'status'),
        }),
        ('Інше', {
            'fields': ('info',),
        }),
    )
