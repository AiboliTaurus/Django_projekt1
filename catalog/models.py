# catalog/models.py
from django.db import models
from django.conf import settings


class Category(models.Model):
    """Модель категории товаров для магазина Skystore"""
    name = models.CharField(
        max_length=150,
        verbose_name='Наименование',
        help_text='Введите название категории (макс. 150 символов)'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Введите описание категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара для магазина Skystore"""
    name = models.CharField(
        max_length=150,
        verbose_name='Наименование',
        help_text='Введите название товара (макс. 150 символов)'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Введите подробное описание товара'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
        blank=True,
        null=True,
        help_text='Загрузите изображение товара'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        blank=True,
        null=True,
        related_name='products',
        help_text='Выберите категорию товара'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        help_text='Введите цену товара в рублях'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    # Статус публикации (для модерации)
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
        help_text='Отметьте, чтобы опубликовать товар'
    )

    # Владелец продукта (ForeignKey на пользователя)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='products',
        null=True,
        blank=True,
        help_text='Владелец товара'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name', '-created_at']

        # КАСТОМНЫЕ ПРАВА
        permissions = [
            ('can_unpublish_product', 'Может отменять публикацию продукта'),
            ('can_delete_any_product', 'Может удалять любой продукт'),
        ]

    def __str__(self):
        return f'{self.name} - {self.price} руб.'


class Contact(models.Model):
    """Модель контактных данных магазина Skystore"""
    name = models.CharField(
        max_length=100,
        verbose_name='Имя контактного лица'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    message = models.TextField(
        verbose_name='Сообщение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone})'
