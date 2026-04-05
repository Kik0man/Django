from django.contrib import admin
from catalog.models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")
    search_fields = ("category_name", "category_description",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product_name", "product_price", "product_category", "product_photo_preview")
    list_filter = ("product_category",)
    search_fields = ("product_name", "product_description",)

    def product_photo_preview(self, obj):
        if obj.product_photo:
            return f'<img src="{obj.product_photo.url}" width="50" height="50" style="object-fit: cover;" />'
        return "Нет фото"

    product_photo_preview.allow_tags = True
    product_photo_preview.short_description = "Превью"