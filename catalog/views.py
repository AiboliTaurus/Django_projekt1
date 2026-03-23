# catalog/views.py - ОБНОВЛЕННАЯ ВЕРСИЯ С КЭШИРОВАНИЕМ

from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.conf import settings

from .models import Product, Contact, Category
from .forms import ProductForm
from .services import get_product_by_id, clear_product_cache, get_products_by_category


class HomeView(ListView):
    """Главная страница магазина Skystore"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """Получаем товары с учетом поиска и фильтрации с низкоуровневым кэшированием"""

        #  НИЗКОУРОВНЕВОЕ КЭШИРОВАНИЕ СПИСКА ВСЕХ ПРОДУКТОВ
        cache_key = 'all_products_list'

        if settings.CACHE_ENABLED:
            all_products = cache.get(cache_key)
            if all_products is not None:
                print(f"✅ КЭШ: Список всех продуктов получен из кэша")
            else:
                all_products = list(Product.objects.all().select_related('category', 'owner'))
                cache.set(cache_key, all_products, timeout=300)
                print(f"💾 КЭШ: Список всех продуктов сохранен в кэш")
        else:
            all_products = list(Product.objects.all().select_related('category', 'owner'))

        # Фильтруем по правам доступа
        queryset = all_products.copy()

        if not self.request.user.has_perm('catalog.can_unpublish_product'):
            queryset = [p for p in queryset if p.is_published]

        # Поиск
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = [
                p for p in queryset
                if search_query.lower() in p.name.lower() or
                   (p.description and search_query.lower() in p.description.lower())
            ]
            self.search_query = search_query

        # Фильтр по категории
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = [p for p in queryset if p.category and p.category.name == category_name]
            self.current_category = category_name

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Главная'
        context['product_count'] = len([p for p in self.get_queryset() if p.is_published])

        if hasattr(self, 'search_query'):
            context['search_query'] = self.search_query
        if hasattr(self, 'current_category'):
            context['current_category'] = self.current_category

        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара - С КЭШИРОВАНИЕМ"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        """ ИСПОЛЬЗУЕМ СЕРВИСНУЮ ФУНКЦИЮ С КЭШИРОВАНИЕМ"""
        product_id = self.kwargs.get('pk')
        return get_product_by_id(product_id)

    def get_queryset(self):
        """Показываем неопубликованные товары только владельцам и модераторам"""
        user = self.request.user

        if user.is_authenticated:
            if user.has_perm('catalog.can_unpublish_product'):
                return Product.objects.all()
            return Product.objects.filter(models.Q(is_published=True) | models.Q(owner=user))
        return Product.objects.filter(is_published=True)

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
        """Автоматически устанавливаем владельца при создании и очищаем кэш"""
        form.instance.owner = self.request.user
        form.instance.is_published = False
        response = super().form_valid(form)

        #  ОЧИЩАЕМ КЭШ ПРИ СОЗДАНИИ ПРОДУКТА
        clear_product_cache(category_name=form.instance.category.name if form.instance.category else None)

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
        #  ОЧИЩАЕМ КЭШ ПРИ ОБНОВЛЕНИИ ПРОДУКТА
        clear_product_cache(product_id=self.object.pk,
                            category_name=self.object.category.name if self.object.category else None)
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
        old_category = self.object.category.name if self.object.category else None

        response = super().delete(request, *args, **kwargs)

        #  ОЧИЩАЕМ КЭШ ПРИ УДАЛЕНИИ ПРОДУКТА
        clear_product_cache(category_name=old_category)

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

        #  ОЧИЩАЕМ КЭШ ПРИ ОТМЕНЕ ПУБЛИКАЦИИ
        clear_product_cache(product_id=pk, category_name=product.category.name if product.category else None)

        messages.success(request, f'Публикация товара "{product.name}" отменена')

        return redirect('catalog:product_detail', pk=product.pk)


class CategoryProductsView(ListView):
    """ НОВОЕ ПРЕДСТАВЛЕНИЕ: Список продуктов в указанной категории"""
    model = Product
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """ ИСПОЛЬЗУЕМ СЕРВИСНУЮ ФУНКЦИЮ С КЭШИРОВАНИЕМ"""
        category_name = self.kwargs.get('category_name')
        self.category = get_object_or_404(Category, name=category_name)
        return get_products_by_category(category_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.category.name} - Skystore'
        context['category'] = self.category
        return context


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
