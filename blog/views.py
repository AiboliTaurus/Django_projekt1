# blog/views.py

from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View  # ✅ ДОБАВЛЕНО
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404  # ✅ ДОБАВЛЕНО
from django.core.exceptions import PermissionDenied

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

    def get_queryset(self):
        """Показываем неопубликованные статьи только контент-менеджерам"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated and user.has_perm('blog.can_manage_blog'):
            return queryset
        return queryset.filter(is_published=True)

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
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            print(f"✅ Email отправлен для статьи '{post.title}'")
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")


class BlogPostCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание новой статьи блога - ТОЛЬКО ДЛЯ КОНТЕНТ-МЕНЕДЖЕРОВ"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')
    login_url = 'users:login'
    success_message = 'Статья "%(title)s" успешно создана!'

    permission_required = 'blog.add_blogpost'

    def form_valid(self, form):
        """Дополнительная логика при успешной валидации"""
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {'title': self.object.title})
        return response


class BlogPostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование статьи блога - ТОЛЬКО ДЛЯ КОНТЕНТ-МЕНЕДЖЕРОВ"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    login_url = 'users:login'
    success_message = 'Статья "%(title)s" успешно обновлена!'

    permission_required = 'blog.change_blogpost'

    def get_success_url(self):
        """После успешного редактирования перенаправляем на страницу статьи"""
        return reverse_lazy('blog:blog_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Дополнительная логика при успешной валидации"""
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {'title': self.object.title})
        return response


class BlogPostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление статьи блога - ТОЛЬКО ДЛЯ КОНТЕНТ-МЕНЕДЖЕРОВ"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')
    login_url = 'users:login'

    permission_required = 'blog.delete_blogpost'

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение при успешном удалении"""
        self.object = self.get_object()
        post_title = self.object.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Статья "{post_title}" успешно удалена!')
        return response


class BlogPostPublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Публикация статьи (для контент-менеджеров)"""

    permission_required = 'blog.can_publish_blogpost'

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)

        post.is_published = True
        post.save()
        messages.success(request, f'Статья "{post.title}" опубликована!')

        return redirect('blog:blog_detail', pk=post.pk)
