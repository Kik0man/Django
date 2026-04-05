from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
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
        messages.success(request, 'Сообщение отправлено!')
        return self.render_to_response(context)


class ProductListView(ListView):
    """Список продуктов с пагинацией"""
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'page_obj'
    paginate_by = 5
    ordering = ['id']

    def get_queryset(self):
        """Получение отсортированного queryset"""
        return super().get_queryset().order_by('id')


class ProductDetailView(DetailView):
    """Детальная страница продукта"""
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'


class ProductCreateView(CreateView):
    """Создание нового продукта с валидацией"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        """Дополнительная обработка при успешном сохранении"""
        messages.success(self.request, 'Продукт успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка невалидной формы"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Ошибка в поле {field}: {error}')
        return super().form_invalid(form)


class ProductUpdateView(UpdateView):
    """Редактирование продукта с валидацией"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Ошибка в поле {field}: {error}')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context