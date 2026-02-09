from django.core.management.base import BaseCommand
from catalog.models import Category, Product, Contact
from decimal import Decimal
import os


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для Skystore'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Начинаем заполнение базы данных Skystore...'))

        # 1. Удаляем существующие данные
        self.stdout.write('Удаляем старые данные...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        Contact.objects.all().delete()

        # 2. Создаем категории
        categories = [
            {
                'name': 'Смартфоны',
                'description': 'Мобильные телефоны и аксессуары'
            },
            {
                'name': 'Ноутбуки',
                'description': 'Портативные компьютеры'
            },
            {
                'name': 'Телевизоры',
                'description': 'Телевизоры и медиатехника'
            },
            {
                'name': 'Аудиотехника',
                'description': 'Наушники, колонки, аудиосистемы'
            },
            {
                'name': 'Бытовая техника',
                'description': 'Техника для дома'
            },
        ]

        created_categories = {}
        for cat_data in categories:
            category = Category.objects.create(**cat_data)
            created_categories[cat_data['name']] = category
            self.stdout.write(f'✓ Создана категория: {category.name}')

        # 3. Создаем товары
        products = [
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'Флагманский смартфон Apple с динамическим островом',
                'category': created_categories['Смартфоны'],
                'price': Decimal('129999.00')
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Смартфон Samsung с пером S-Pen',
                'category': created_categories['Смартфоны'],
                'price': Decimal('119999.00')
            },
            {
                'name': 'Xiaomi 14 Pro',
                'description': 'Флагманский смартфон с камерой Leica',
                'category': created_categories['Смартфоны'],
                'price': Decimal('79999.00')
            },
            {
                'name': 'MacBook Pro 16" M3 Max',
                'description': 'Ноутбук Apple для профессиональной работы',
                'category': created_categories['Ноутбуки'],
                'price': Decimal('299999.00')
            },
            {
                'name': 'ASUS ROG Strix G18',
                'description': 'Игровой ноутбук с RTX 4080',
                'category': created_categories['Ноутбуки'],
                'price': Decimal('219999.00')
            },
            {
                'name': 'LG OLED C3',
                'description': '4K OLED телевизор с технологией AI Processor',
                'category': created_categories['Телевизоры'],
                'price': Decimal('149999.00')
            },
            {
                'name': 'Samsung QLED Q80C',
                'description': 'Телевизор QLED 4K с технологией Quantum HDR',
                'category': created_categories['Телевизоры'],
                'price': Decimal('89999.00')
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Беспроводные наушники с шумоподавлением',
                'category': created_categories['Аудиотехника'],
                'price': Decimal('29999.00')
            },
            {
                'name': 'Apple AirPods Pro 2',
                'description': 'Беспроводные наушники с активным шумоподавлением',
                'category': created_categories['Аудиотехника'],
                'price': Decimal('24999.00')
            },
            {
                'name': 'Dyson V15 Detect',
                'description': 'Пылесос с лазерной системой обнаружения пыли',
                'category': created_categories['Бытовая техника'],
                'price': Decimal('69999.00')
            },
        ]

        for prod_data in products:
            product = Product.objects.create(**prod_data)
            self.stdout.write(f'✓ Создан товар: {product.name} - {product.price} руб.')

        # 4. Создаем контакты
        contacts = [
            {
                'name': 'Александр Иванов',
                'phone': '+7 (999) 111-22-33',
                'message': 'Интересует наличие iPhone 15 в синем цвете'
            },
            {
                'name': 'Мария Петрова',
                'phone': '+7 (999) 222-33-44',
                'message': 'Есть ли доставка в Санкт-Петербург?'
            },
            {
                'name': 'Дмитрий Сидоров',
                'phone': '+7 (999) 333-44-55',
                'message': 'Нужна консультация по выбору игрового ноутбука'
            },
        ]

        for contact_data in contacts:
            contact = Contact.objects.create(**contact_data)
            self.stdout.write(f'✓ Создан контакт: {contact.name} - {contact.phone}')

        # 5. Выводим статистику
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

        stats = f"""
        📊 Статистика Skystore:
        -------------------------
        Категорий: {Category.objects.count()}
        Товаров: {Product.objects.count()}
        Контактов: {Contact.objects.count()}
        -------------------------
        """
        self.stdout.write(stats)

        # 6. Альтернативный вариант: загрузка из фикстур
        # from django.core.management import call_command
        # self.stdout.write('\nАльтернатива: загружаем данные из фикстур...')
        # call_command('loaddata', 'fixtures/all_catalog_data.json')