# blog/views.py
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from config import settings
from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """Список всех опубликованных статей блога - ОБЩЕДОСТУПНО"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        """Выводим только опубликованные статьи"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogPostDetailView(DetailView):
    """Детальная страница статьи блога - ОБЩЕДОСТУПНО"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Переопределяем для увеличения счетчика просмотров"""
        obj = super().get_object(queryset)

        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        # Отправка email при 100 просмотрах
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
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],  # Отправляем себе
                fail_silently=False,
            )
            print(f"✅ Email отправлен для статьи '{post.title}'")
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")


class BlogPostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание новой статьи блога - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')
    login_url = 'users:login'
    success_message = 'Статья "%(title)s" успешно создана!'

    def form_valid(self, form):
        """Дополнительная логика при успешной валидации"""
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {'title': self.object.title})
        return response


class BlogPostUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование статьи блога - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    login_url = 'users:login'
    success_message = 'Статья "%(title)s" успешно обновлена!'

    def get_success_url(self):
        """После успешного редактирования перенаправляем на страницу статьи"""
        return reverse_lazy('blog:blog_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Дополнительная логика при успешной валидации"""
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {'title': self.object.title})
        return response


class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление статьи блога - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')
    login_url = 'users:login'

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение при успешном удалении"""
        self.object = self.get_object()
        post_title = self.object.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Статья "{post_title}" успешно удалена!')
        return response
