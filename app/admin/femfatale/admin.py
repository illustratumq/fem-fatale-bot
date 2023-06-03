from django.contrib import admin
from .models import Partner, User, Media, Article, BaseForm


@admin.register(Partner)
class UserAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('name', 'id', 'category', 'cashback', 'city', 'updated_at')
    list_filter = ('city', 'category')
    search_fields = ("name__startswith",)
    ordering = ['-updated_at']


@admin.register(Article)
class UserAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('title', 'status', 'id', 'media_id', 'updated_at')
    list_filter = ('status',)
    search_fields = ("name__startswith",)
    ordering = ['-updated_at']


@admin.register(Media)
class UserAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('name', 'id', 'created_at')
    ordering = ['-created_at']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    form = BaseForm

    list_display = ('full_name', 'card', 'phone', 'balance', 'role', 'status', 'updated_at')
    list_filter = ('status', 'role')
    search_fields = ("card__startswith", "full_name__startswith")
    ordering = ['-updated_at']

