from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator  # Добавляем импорт
from .models import Product, Contact, Category
from .forms import ProductForm  # Добавляем импорт
from django.contrib import messages


def product_create(request):
    """Страница добавления нового товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем товар в БД
            product = form.save()

            # Добавляем сообщение об успехе
            messages.success(request, f'Товар "{product.name}" успешно добавлен!')

            # Перенаправляем на страницу нового товара
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()

    # Получаем все категории для отображения (опционально)
    categories = Category.objects.all()

    context = {
        'title': 'Добавление товара - Skystore',
        'form': form,
        'categories': categories,
    }
    return render(request, 'catalog/product_form.html', context)


def home(request):
    """Главная страница магазина Skystore с пагинацией"""
    # Получаем ВСЕ товары, отсортированные по дате создания
    products_list = Product.objects.all().order_by('-created_at')

    # ПАГИНАЦИЯ: 6 товаров на страницу
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page', 1)  # Получаем номер страницы из URL
    page_obj = paginator.get_page(page_number)

    # Выводим в консоль для отладки
    print("=" * 50)
    print(f"SKYSTORE: Всего товаров: {products_list.count()}")
    print(f"Страница {page_obj.number} из {paginator.num_pages}")
    print(f"Товаров на странице: {len(page_obj)}")
    print("=" * 50)
    print("Товары на этой странице:")
    for product in page_obj:
        category_name = product.category.name if product.category else "Без категории"
        print(f"  - {product.name}: {product.price} руб. (Категория: {category_name})")
    print("=" * 50)

    context = {
        'title': 'Skystore - Главная',
        'page_obj': page_obj,  # Передаём объект страницы для пагинации
        'products': page_obj,  # Для обратной совместимости с шаблоном
        'product_count': products_list.count(),  # Общее количество товаров
        'is_paginated': page_obj.has_other_pages(),  # Есть ли другие страницы
    }
    return render(request, 'catalog/home.html', context)


def product_detail(request, pk):
    """Детальная страница товара"""
    product = get_object_or_404(Product, pk=pk)

    context = {
        'title': f'{product.name} - Skystore',
        'product': product,
    }
    return render(request, 'catalog/product_detail.html', context)


def contacts(request):
    """Страница контактов магазина Skystore"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print(f'Сообщение от {name} ({phone}): {message}')

        if name and phone and message:
            contact = Contact.objects.create(
                name=name,
                phone=phone,
                message=message
            )
            print(f'Контакт сохранён в БД с ID: {contact.id}')

        return HttpResponseRedirect('/contacts/?success=true')

    contacts_list = Contact.objects.all().order_by('-created_at')

    context = {
        'title': 'Skystore - Контакты',
        'contacts': contacts_list,
    }
    return render(request, 'catalog/contacts.html', context)
