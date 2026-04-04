from django.core.management.base import BaseCommand
from django.db import connection
from catalog.models import Category, Product
from datetime import datetime


class Command(BaseCommand):
    help = "Add test products to database"

    def handle(self, *args, **options):
        self.stdout.write("Удаляем старые данные...")

        Product.objects.all().delete()
        Category.objects.all().delete()

        # Сбрасываем счетчик ID для Product
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE catalog_product_id_seq RESTART WITH 1;")

        self.stdout.write("Создаем категории...")

        electronics = Category.objects.create(
            category_name="Электроника",
            category_description="Гаджеты и техника"
        )

        clothes = Category.objects.create(
            category_name="Одежда",
            category_description="Повседневная одежда"
        )

        self.stdout.write("Создаем продукты...")

        products = [
            {
                "product_name": "iPhone 15",
                "product_description": "Смартфон Apple",
                "product_category": electronics,
                "product_price": 1000,
            },
            {
                "product_name": "Футболка",
                "product_description": "Белая футболка",
                "product_category": clothes,
                "product_price": 20,
            },
        ]

        for product_data in products:
            product = Product.objects.create(**product_data)
            self.stdout.write(
                self.style.SUCCESS(f"Добавлен продукт: {product.product_name} (ID: {product.id})")
            )