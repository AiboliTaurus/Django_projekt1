# blog/admin.py
from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_published', 'views_count', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('views_count', 'created_at')
    list_editable = ('is_published',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'preview')
        }),
        ('Настройки публикации', {
            'fields': ('is_published', 'views_count', 'created_at')
        }),
    )
