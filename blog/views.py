# blog/views.py
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404

from config import settings
from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """Список всех опубликованных статей блога"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9  # 9 статей на странице

    def get_queryset(self):
        """Выводим только опубликованные статьи"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogPostDetailView(DetailView):
    """Детальная страница статьи блога"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Переопределяем для увеличения счетчика просмотров"""
        obj = super().get_object(queryset)

        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        # Дополнительное задание: отправка email при 100 просмотрах
        if obj.views_count == 100:
            self.send_congratulatory_email(obj)

        return obj

    def send_congratulatory_email(self, post):
        """Отправка поздравления при достижении 100 просмотров"""
        subject = f'🎉 Поздравляем! Статья достигла 100 просмотров!'
        message = f'''
        Здравствуйте!

        Ваша статья "{post.title}" достигла 100 просмотров!

        Детали статьи:
        - Заголовок: {post.title}
        - Количество просмотров: {post.views_count}
        - Дата создания: {post.created_at.strftime('%d.%m.%Y')}

        Ссылка на статью: http://localhost:8000/blogs/{post.pk}/

        Продолжайте в том же духе!

        С уважением,
        Команда Skystore
        '''

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  # Отправляем себе
                fail_silently=False,
            )
            print(f"✅ Email отправлен для статьи '{post.title}'")
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")


class BlogPostCreateView(CreateView):
    """Создание новой статьи блога"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')


class BlogPostUpdateView(UpdateView):
    """Редактирование статьи блога"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'

    def get_success_url(self):
        """После успешного редактирования перенаправляем на страницу статьи"""
        return reverse_lazy('blog:blog_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    """Удаление статьи блога"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')