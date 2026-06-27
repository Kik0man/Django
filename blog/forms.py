from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    """Форма для блоговой записи"""

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Введите текст статьи', 'rows': 10}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
            'preview': 'Превью (изображение)',
            'is_published': 'Опубликовать',
        }