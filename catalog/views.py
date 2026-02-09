from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product, Contact


def home(request):
    """Главная страница магазина Skystore"""
    # Получаем последние 5 товаров
    latest_products = Product.objects.all().order_by('-created_at')[:5]

    # ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ: Выводим в консоль
    print("=" * 50)
    print("SKYSTORE: Последние 5 добавленных товаров:")
    for product in latest_products:
        category_name = product.category.name if product.category else "Без категории"
        print(f"  - {product.name}: {product.price} руб. (Категория: {category_name})")
    print("=" * 50)

    context = {
        'title': 'Skystore - Главная',
        'products': latest_products,
        'product_count': Product.objects.count(),
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    """Страница контактов магазина Skystore"""
    # Обработка POST-запроса (форма отправки контакта)
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Выводим в консоль (старый функционал)
        print(f'Сообщение от {name} ({phone}): {message}')

        # Сохраняем в БД (новый функционал)
        if name and phone and message:  # Проверяем, что все поля заполнены
            contact = Contact.objects.create(
                name=name,
                phone=phone,
                message=message
            )
            print(f'Контакт сохранён в БД с ID: {contact.id}')

        # Перенаправляем с флагом успеха
        return HttpResponseRedirect('/contacts/?success=true')

    # GET-запрос: отображаем страницу с контактами из БД
    contacts_list = Contact.objects.all().order_by('-created_at')

    context = {
        'title': 'Skystore - Контакты',
        'contacts': contacts_list,
    }
    return render(request, 'catalog/contacts.html', context)