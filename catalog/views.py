# catalog/views.py - С LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect

from .models import Product, Contact, Category
from .forms import ProductForm


class HomeView(ListView):
    """Главная страница магазина Skystore с пагинацией, фильтрацией по категориям и поиском"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """Получаем товары с учетом поискового запроса и фильтра по категории"""
        queryset = Product.objects.all().order_by('-created_at')

        # ПОИСК по названию и описанию
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
            self.search_query = search_query

        # ФИЛЬТР по категории
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(category__name=category_name)
            self.current_category = category_name

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Главная'
        context['product_count'] = Product.objects.count()

        # Добавляем информацию о поиске
        if hasattr(self, 'search_query'):
            context['search_query'] = self.search_query

        # Добавляем информацию о категории
        if hasattr(self, 'current_category'):
            context['current_category'] = self.current_category

        # Добавляем все категории для меню
        context['categories'] = Category.objects.all()

        return context


class ProductDetailView(DetailView):
    """Детальная страница товара - ОБЩЕДОСТУПНА"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.object.name} - Skystore"

        # Добавляем похожие товары (из той же категории)
        if self.object.category:
            context['related_products'] = Product.objects.filter(
                category=self.object.category
            ).exclude(pk=self.object.pk)[:4]
        else:
            context['related_products'] = []

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Страница добавления нового товара - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'  # Куда перенаправлять неавторизованных

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление товара - Skystore'
        context['categories'] = Category.objects.all()
        context['is_update'] = False
        return context

    def form_valid(self, form):
        """Дополнительная логика при успешной валидации"""
        response = super().form_valid(form)
        messages.success(self.request, f'Товар "{self.object.name}" успешно добавлен!')
        return response

    def form_invalid(self, form):
        """Логика при невалидной форме"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования товара - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.name} - Skystore'
        context['categories'] = Category.objects.all()
        context['is_update'] = True
        return context

    def get_success_url(self):
        """Перенаправляем на страницу товара после редактирования"""
        messages.success(self.request, f'Товар "{self.object.name}" успешно обновлён!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        """Логика при невалидной форме"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Страница подтверждения удаления товара - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление: {self.object.name} - Skystore'
        return context

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение при успешном удалении"""
        self.object = self.get_object()
        product_name = self.object.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Товар "{product_name}" успешно удалён!')
        return response


class ContactsView(TemplateView):
    """Страница контактов магазина Skystore"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Контакты'
        context['contacts'] = Contact.objects.all().order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса (отправка формы)"""
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        if name and phone and message:
            Contact.objects.create(
                name=name,
                phone=phone,
                message=message
            )

        return redirect(f'{reverse_lazy("catalog:contacts")}?success=true')
