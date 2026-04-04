from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'home.html'


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'contacts.html'

    def post(self, request, *args, **kwargs):
        # Обработка POST запроса для формы обратной связи
        context = self.get_context_data(**kwargs)
        # Здесь можно добавить логику отправки сообщения
        # Например: отправка email, сохранение в БД и т.д.
        return self.render_to_response(context)


class ProductListView(ListView):
    """Список продуктов с пагинацией"""
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'page_obj'  # Сохраняем имя для совместимости с шаблоном
    paginate_by = 5
    ordering = ['id']  # Сортировка по id

    def get_queryset(self):
        """Получение отсортированного queryset"""
        return super().get_queryset().order_by('id')

    def get_context_data(self, **kwargs):
        """Добавляем page_obj в контекст для совместимости с шаблоном"""
        context = super().get_context_data(**kwargs)
        return context


class ProductDetailView(DetailView):
    """Детальная страница продукта"""
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'


class ProductCreateView(CreateView):
    """Создание нового продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        """Дополнительная обработка при успешном сохранении"""
        return super().form_valid(form)