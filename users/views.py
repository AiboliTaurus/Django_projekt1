# users/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.conf import settings

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


class UserRegistrationView(SuccessMessageMixin, CreateView):
    """
    Контроллер регистрации пользователя
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Регистрация прошла успешно! Теперь вы можете войти в систему.'

    def form_valid(self, form):
        """Отправка приветственного письма после успешной регистрации"""
        response = super().form_valid(form)

        # Отправка приветственного письма
        self.send_welcome_email(form.cleaned_data['email'])

        return response

    def send_welcome_email(self, email):
        """Отправка приветственного письма"""
        subject = 'Добро пожаловать в Skystore!'
        message = f'''
        Здравствуйте!

        Спасибо за регистрацию в нашем интернет-магазине Skystore!

        Теперь вы можете:
        - Просматривать каталог товаров
        - Добавлять новые товары
        - Редактировать и удалять свои товары
        - Оставлять комментарии в блоге

        С уважением,
        Команда Skystore
        '''

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            print(f'✅ Приветственное письмо отправлено на {email}')
        except Exception as e:
            print(f'❌ Ошибка отправки письма: {e}')


class UserLoginView(LoginView):
    """
    Контроллер авторизации пользователя
    """
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('catalog:home')


class UserLogoutView(LogoutView):
    """
    Контроллер выхода пользователя
    """
    next_page = reverse_lazy('catalog:home')


class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Контроллер редактирования профиля пользователя (доп. задание)
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_message = 'Профиль успешно обновлен!'

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        """Возвращаем текущего пользователя"""
        return self.request.user
