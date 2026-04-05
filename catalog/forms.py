from django import forms
from django.core.exceptions import ValidationError
from .models import Product
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import io


class ProductForm(forms.ModelForm):
    """Форма для продукта с валидацией запрещенных слов и цены"""

    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_description',
            'product_category',
            'product_price',
            'product_photo'  # Добавляем поле для фото
        ]
        labels = {
            'product_name': 'Наименование продукта',
            'product_description': 'Описание продукта',
            'product_category': 'Категория',
            'product_price': 'Цена (руб.)',
            'product_photo': 'Фото продукта'
        }
        help_texts = {
            'product_price': 'Цена должна быть положительной',
            'product_photo': 'Поддерживаются форматы JPEG, PNG. Максимальный размер 5MB'
        }

    # Список запрещенных слов
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    def __init__(self, *args, **kwargs):
        """Добавляем стилизацию для всех полей формы"""
        super().__init__(*args, **kwargs)

        # Применяем классы Bootstrap к каждому полю
        for field_name, field in self.fields.items():
            if field_name == 'is_published':
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name == 'product_description':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 5
                field.widget.attrs['placeholder'] = 'Введите описание продукта...'
            elif field_name == 'product_photo':
                field.widget.attrs['class'] = 'form-control-file'
                field.widget.attrs['accept'] = 'image/jpeg,image/png'
            else:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

    def clean_product_name(self):
        """Валидация названия продукта на запрещенные слова"""
        product_name = self.cleaned_data.get('product_name')

        if product_name:
            # Проверяем наличие запрещенных слов (игнорируем регистр)
            product_name_lower = product_name.lower()

            for forbidden_word in self.FORBIDDEN_WORDS:
                if forbidden_word in product_name_lower:
                    raise ValidationError(
                        f'Название продукта содержит запрещенное слово "{forbidden_word}". '
                        f'Пожалуйста, удалите его.'
                    )

        return product_name

    def clean_product_description(self):
        """Валидация описания продукта на запрещенные слова"""
        product_description = self.cleaned_data.get('product_description')

        if product_description:
            # Проверяем наличие запрещенных слов (игнорируем регистр)
            description_lower = product_description.lower()

            for forbidden_word in self.FORBIDDEN_WORDS:
                if forbidden_word in description_lower:
                    raise ValidationError(
                        f'Описание продукта содержит запрещенное слово "{forbidden_word}". '
                        f'Пожалуйста, удалите его.'
                    )

        return product_description

    def clean_product_price(self):
        """Валидация цены продукта (не может быть отрицательной)"""
        product_price = self.cleaned_data.get('product_price')

        if product_price is not None:
            if product_price < 0:
                raise ValidationError('Цена продукта не может быть отрицательной.')
            elif product_price == 0:
                raise ValidationError('Цена продукта должна быть больше нуля.')
            elif product_price > 1_000_000:
                raise ValidationError('Цена продукта не может превышать 1 000 000 рублей.')

        return product_price

    def clean_product_photo(self):
        """Валидация загружаемого изображения"""
        photo = self.cleaned_data.get('product_photo')

        if photo:
            # Проверка размера файла (максимум 5 МБ = 5 * 1024 * 1024 байт)
            max_size = 5 * 1024 * 1024  # 5MB

            if photo.size > max_size:
                raise ValidationError(
                    f'Размер файла не должен превышать 5 МБ. '
                    f'Ваш файл: {photo.size / (1024 * 1024):.2f} МБ'
                )

            # Проверка формата файла
            valid_formats = ['image/jpeg', 'image/png', 'image/jpg']

            if hasattr(photo, 'content_type'):
                if photo.content_type not in valid_formats:
                    raise ValidationError(
                        'Неподдерживаемый формат файла. '
                        'Пожалуйста, загрузите файл в формате JPEG или PNG.'
                    )

            # Дополнительная проверка с помощью PIL
            try:
                # Открываем изображение
                image = Image.open(photo)

                # Проверяем формат
                if image.format not in ['JPEG', 'PNG']:
                    raise ValidationError(
                        'Неподдерживаемый формат изображения. '
                        'Используйте JPEG или PNG.'
                    )

                # Опционально: проверяем размеры изображения
                max_width = 2000
                max_height = 2000

                if image.width > max_width or image.height > max_height:
                    raise ValidationError(
                        f'Размеры изображения не должны превышать {max_width}x{max_height} пикселей. '
                        f'Ваше изображение: {image.width}x{image.height}'
                    )

                # Если нужно оптимизировать изображение
                # Это дополнительная функция для сжатия
                photo = self.optimize_image(photo, image)

            except Exception as e:
                raise ValidationError(f'Ошибка при обработке изображения: {str(e)}')

        return photo

    def optimize_image(self, photo, image):
        """Оптимизация изображения (сжатие)"""
        # Создаем буфер для оптимизированного изображения
        output = io.BytesIO()

        # Конвертируем в RGB если необходимо (для PNG с альфа-каналом)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')

        # Сохраняем с оптимизацией
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)

        # Создаем новый InMemoryUploadedFile
        optimized_photo = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{photo.name.split('.')[0]}.jpg",
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )

        return optimized_photo