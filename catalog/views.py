# catalog/views.py
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Product, Contact, Category
from .forms import ProductForm


class HomeView(ListView):
    """Главная страница магазина Skystore"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """Получаем товары с учетом поиска и фильтрации"""
        queryset = Product.objects.all().order_by('-created_at')

        # Фильтруем только опубликованные товары для обычных пользователей
        if not self.request.user.has_perm('catalog.can_unpublish_product'):
            queryset = queryset.filter(is_published=True)

        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
            self.search_query = search_query

        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(category__name=category_name)
            self.current_category = category_name

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Главная'
        context['product_count'] = Product.objects.filter(is_published=True).count()

        if hasattr(self, 'search_query'):
            context['search_query'] = self.search_query
        if hasattr(self, 'current_category'):
            context['current_category'] = self.current_category

        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Показываем неопубликованные товары только владельцам и модераторам"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            if user.has_perm('catalog.can_unpublish_product'):
                return queryset
            return queryset.filter(models.Q(is_published=True) | models.Q(owner=user))
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.object.name} - Skystore"

        if self.object.category:
            context['related_products'] = Product.objects.filter(
                category=self.object.category,
                is_published=True
            ).exclude(pk=self.object.pk)[:4]
        else:
            context['related_products'] = []

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление товара - Skystore'
        context['categories'] = Category.objects.all()
        context['is_update'] = False
        return context

    def form_valid(self, form):
        """Автоматически устанавливаем владельца при создании"""
        form.instance.owner = self.request.user
        form.instance.is_published = False
        response = super().form_valid(form)
        messages.success(self.request, f'Товар "{self.object.name}" успешно добавлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = 'users:login'

    def dispatch(self, request, *args, **kwargs):
        """Проверяем права перед обработкой запроса"""
        obj = self.get_object()

        if not (request.user == obj.owner or request.user.has_perm('catalog.can_unpublish_product')):
            raise PermissionDenied("У вас нет прав для редактирования этого товара")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.name} - Skystore'
        context['categories'] = Category.objects.all()
        context['is_update'] = True
        return context

    def get_success_url(self):
        messages.success(self.request, f'Товар "{self.object.name}" успешно обновлён!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'

    def dispatch(self, request, *args, **kwargs):
        """Проверяем права перед удалением"""
        obj = self.get_object()

        can_delete = (
                request.user == obj.owner or
                request.user.has_perm('catalog.delete_product') or
                request.user.has_perm('catalog.can_delete_any_product')
        )

        if not can_delete:
            raise PermissionDenied("У вас нет прав для удаления этого товара")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление: {self.object.name} - Skystore'
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        product_name = self.object.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Товар "{product_name}" успешно удалён!')
        return response


class ProductUnpublishView(LoginRequiredMixin, View):
    """Отмена публикации товара"""

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if not request.user.has_perm('catalog.can_unpublish_product'):
            raise PermissionDenied("У вас нет прав для отмены публикации")

        product.is_published = False
        product.save()
        messages.success(request, f'Публикация товара "{product.name}" отменена')

        return redirect('catalog:product_detail', pk=product.pk)


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Контакты'
        context['contacts'] = Contact.objects.all().order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
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
    