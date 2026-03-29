from django.db import models


class Category(models.Model):
    category_name = (
        models.CharField(
            max_length=150,
            verbose_name="Название категории",
            help_text="Введите категорию продукта",
        )
    )
    category_description = (
        models.TextField(
            verbose_name="Описание категории",
            help_text="Опишите категорию",
            blank=True,
            null=True,
        )
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = (
        models.CharField(
            max_length=150,
            verbose_name="Наименование продукта",
            help_text="Введите наименование продукта",
        )
    )
    product_description = (
        models.TextField(
            verbose_name="Описание", help_text="Опишите продукт", blank=True, null=True
        )
    )
    product_photo = models.ImageField(
        upload_to="products/photo",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото",
    )
    product_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория продукта",
        help_text="Введите категорию продукта",
        null=True,
        blank=True,
        related_name="products",
    )
    product_price = models.IntegerField(
        verbose_name="Цена за покупку",
        help_text="ВВедите цену продукта",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата последнего изменения",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["product_category", "product_price"]

    def __str__(self):
        return self.product_name
