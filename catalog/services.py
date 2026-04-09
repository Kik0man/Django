from django.core.cache import cache
from .models import Product, Category

def get_products_by_category(category_id):
    """Вернуть список продуктов в указанной категории с кешированием на 10 минут."""
    cache_key = f'products_category_{category_id}'
    products = cache.get(cache_key)
    if products is None:
        try:
            category = Category.objects.get(pk=category_id)
            products = list(Product.objects.filter(product_category=category))
        except Category.DoesNotExist:
            products = []
        cache.set(cache_key, products, 60 * 10)  # 10 минут
    return products