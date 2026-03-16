from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для кастомной модели пользователя"""
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_display_links = ('id', 'email')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'country')
    ordering = ('email',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'password')
        }),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name', 'avatar', 'phone_number', 'country')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
