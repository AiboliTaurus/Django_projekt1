# blog/models.py
from django.db import models
from django.urls import reverse


class BlogPost(models.Model):
    """Модель блоговой записи"""
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Введите заголовок статьи'
    )
    content = models.TextField(
        verbose_name='Содержимое',
        help_text='Введите содержимое статьи'
    )
    preview = models.ImageField(
        upload_to='blog/',
        verbose_name='Превью',
        blank=True,
        null=True,
        help_text='Загрузите изображение для превью'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
        help_text='Отметьте, чтобы опубликовать статью'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров',
        help_text='Счетчик просмотров статьи'
    )

    class Meta:
        verbose_name = 'Блоговая запись'
        verbose_name_plural = 'Блоговые записи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Возвращает URL для детального просмотра статьи"""
        return reverse('blog:blogpost_detail', kwargs={'pk': self.pk})