# catalog/services.py

from django.core.cache import cache
from django.urls import reverse
from django.conf import settings
from .models import Product, Category


def clear_page_cache(product=None, category_name=None):
    """
    Очищает кэш страниц при изменении данных
    """
    # Очистить кэш главной страницы
    try:
        cache.delete(reverse('catalog:home'))
        print(f"🗑️ КЭШ: Очищен кэш главной страницы")
    except Exception as e:
        print(f"⚠️ Ошибка очистки кэша главной страницы: {e}")

    # Очистить кэш категории
    if category_name:
        try:
            cache.delete(reverse('catalog:category_products', args=[category_name]))
            print(f"🗑️ КЭШ: Очищен кэш категории '{category_name}'")
        except Exception as e:
            print(f"⚠️ Ошибка очистки кэша категории: {e}")

    # Очистить кэш детальной страницы товара
    if product and hasattr(product, 'pk'):
        try:
            cache.delete(reverse('catalog:product_detail', args=[product.pk]))
            print(f"🗑️ КЭШ: Очищен кэш детальной страницы товара ID={product.pk}")
        except Exception as e:
            print(f"⚠️ Ошибка очистки кэша детальной страницы: {e}")


def get_products_by_category(category_name):
    """
    Сервисная функция для получения списка продуктов в указанной категории.
    Использует низкоуровневое кэширование.
    """
    # Ключ кэша для списка продуктов по категории
    cache_key = f'products_by_category_{category_name}'

    # Проверяем, включено ли кэширование
    if settings.CACHE_ENABLED:
        # Пытаемся получить данные из кэша
        products = cache.get(cache_key)
        if products is not None:
            print(f"✅ КЭШ: Данные для категории '{category_name}' получены из кэша")
            return products

    # Если данных нет в кэше или кэш отключен - запрашиваем из БД
    print(f"📊 БД: Запрос продуктов в категории '{category_name}' из базы данных")

    try:
        category = Category.objects.get(name=category_name)
        products = list(Product.objects.filter(
            category=category,
            is_published=True
        ).select_related('category', 'owner'))
    except Category.DoesNotExist:
        products = []

    # Сохраняем в кэш на 5 минут (300 секунд), если кэш включен
    if settings.CACHE_ENABLED:
        cache.set(cache_key, products, timeout=300)
        print(f"💾 КЭШ: Данные для категории '{category_name}' сохранены в кэш на 5 минут")

    return products


def get_product_by_id(product_id):
    """
    Сервисная функция для получения одного продукта по ID.
    Использует низкоуровневое кэширование.
    """
    cache_key = f'product_{product_id}'

    if settings.CACHE_ENABLED:
        product = cache.get(cache_key)
        if product is not None:
            print(f"✅ КЭШ: Продукт ID={product_id} получен из кэша")
            return product

    print(f"📊 БД: Запрос продукта ID={product_id} из базы данных")

    try:
        product = Product.objects.select_related('category', 'owner').get(pk=product_id)
    except Product.DoesNotExist:
        product = None

    if settings.CACHE_ENABLED and product:
        cache.set(cache_key, product, timeout=300)
        print(f"💾 КЭШ: Продукт ID={product_id} сохранен в кэш на 5 минут")

    return product


def clear_product_cache(product_id=None, category_name=None):
    """
    Очистка кэша при изменении продукта
    """
    # Очищаем кэш данных продукта
    if product_id:
        cache.delete(f'product_{product_id}')
        print(f"🗑️ КЭШ: Очищен кэш данных для продукта ID={product_id}")

    # Очищаем кэш списка продуктов по категории
    if category_name:
        cache.delete(f'products_by_category_{category_name}')
        print(f"🗑️ КЭШ: Очищен кэш данных для категории '{category_name}'")

    # Очищаем общий кэш списка продуктов
    cache.delete('all_products_list')
    print(f"🗑️ КЭШ: Очищен общий кэш списка продуктов")

    # ОЧИЩАЕМ КЭШ СТРАНИЦ (для кэширования страниц)
    clear_page_cache(
        product=Product.objects.get(pk=product_id) if product_id else None,
        category_name=category_name
    )

    print("🗑️ КЭШ: Кэш страниц и данных полностью очищен")
