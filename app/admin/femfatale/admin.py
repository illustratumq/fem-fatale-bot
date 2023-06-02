from django.contrib import admin
from .models import Partner, User


@admin.register(Partner)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'category', 'cashback', 'city', 'updated_at')
    list_filter = ('city', 'category')
    search_fields = ("name__startswith",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'card', 'phone', 'balance', 'role', 'status', 'updated_at')
    list_filter = ('status', 'role')
    search_fields = ("card__startswith", "full_name__startswith")
    ordering = ['-updated_at']

