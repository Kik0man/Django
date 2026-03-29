from django.core.management.base import BaseCommand
from catalog.models import Category, Product
from datetime import datetime


class Command(BaseCommand):
    help = "Add test products to database"

    def handle(self, *args, **options):
        self.stdout.write("Удаляем старые данные...")

        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Создаем категории...")

        electronics = Category.objects.create(
            category_name="Электроника", category_description="Гаджеты и техника"
        )

        clothes = Category.objects.create(
            category_name="Одежда", category_description="Повседневная одежда"
        )

        self.stdout.write("Создаем продукты...")

        products = [
            {
                "product_name": "iPhone 15",
                "product_description": "Смартфон Apple",
                "product_category": electronics,
                "product_price": 1000,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "product_name": "Футболка",
                "product_description": "Белая футболка",
                "product_category": clothes,
                "product_price": 20,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        for product_data in products:
            product, created = Product.objects.get_or_create(**product_data)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Добавлен продукт: {product.product_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Продукт уже существует: {product.product_name}"
                    )
                )
