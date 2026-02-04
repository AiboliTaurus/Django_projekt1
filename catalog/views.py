from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'catalog/home.html')


def contacts(request):
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f'Сообщение от {name} ({phone}): {message}')
        return HttpResponse('Сообщение отправлено!')
    return render(request, 'catalog/contacts.html')
