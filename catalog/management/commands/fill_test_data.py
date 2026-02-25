# catalog/management/commands/fill_test_data.py
from django.core.management.base import BaseCommand
from catalog.models import Category, Product, Contact
from decimal import Decimal


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
                'name': 'Наушники',  # ЭТА КАТЕГОРИЯ УЖЕ ЕСТЬ
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

        # 3. Создаем товары (ДОБАВЛЯЕМ ТОВАРЫ ДЛЯ НАУШНИКОВ)
        products = [
            # Смартфоны
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
            # Ноутбуки
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
            # Телевизоры
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
            # НАУШНИКИ (НОВЫЕ ТОВАРЫ)
            {
                'name': 'Apple AirPods Pro 2',
                'description': 'Беспроводные наушники с активным шумоподавлением, чип H2',
                'category': created_categories['Наушники'],
                'price': Decimal('24990.00')
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Премиальные беспроводные наушники с шумоподавлением',
                'category': created_categories['Наушники'],
                'price': Decimal('29990.00')
            },
            {
                'name': 'Samsung Galaxy Buds2 Pro',
                'description': 'Компактные беспроводные наушники с 24-бит звуком',
                'category': created_categories['Наушники'],
                'price': Decimal('15990.00')
            },
            {
                'name': 'Marshall Major IV',
                'description': 'Наушники с фирменным звуком Marshall и 80+ часами работы',
                'category': created_categories['Наушники'],
                'price': Decimal('12990.00')
            },
            # Бытовая техника
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

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))