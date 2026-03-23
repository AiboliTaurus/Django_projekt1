# catalog/admin.py - ПОЛНАЯ ВЕРСИЯ С ОЧИСТКОЙ КЭША

from django.contrib import admin
from .models import Category, Product, Contact
from .services import clear_product_cache


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'is_published', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('category', 'created_at', 'is_published')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_published',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('Изображение', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_published', 'owner'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # ДОБАВЛЯЕМ МЕТОД ДЛЯ ОЧИСТКИ КЭША ПРИ СОХРАНЕНИИ
    def save_model(self, request, obj, form, change):
        """Очищаем кэш при сохранении товара через админку"""
        old_category = None

        # Если это изменение существующего товара, запоминаем старую категорию
        if change:
            try:
                old_obj = Product.objects.get(pk=obj.pk)
                old_category = old_obj.category.name if old_obj.category else None
            except Product.DoesNotExist:
                pass

        # Сохраняем товар
        super().save_model(request, obj, form, change)

        # Очищаем кэш
        clear_product_cache(
            product_id=obj.pk,
            category_name=old_category or (obj.category.name if obj.category else None)
        )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    list_display_links = ('name', 'phone')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
