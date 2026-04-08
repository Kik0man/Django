from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product, Category
from .forms import ProductForm
from .services import get_products_by_category
from django.core.cache import cache


class HomeView(TemplateView):
    """Главная страница (общедоступная)"""
    template_name = 'home.html'


class ContactsView(TemplateView):
    """Страница контактов (общедоступная)"""
    template_name = 'contacts.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        messages.success(request, 'Сообщение отправлено!')
        return self.render_to_response(context)


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'page_obj'
    paginate_by = 5

    def get_queryset(self):
        # Ключ кеша может зависеть от номера страницы и параметров сортировки
        page = self.request.GET.get('page', 1)
        cache_key = f'product_list_page_{page}'
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = list(Product.objects.all().order_by('id'))
            cache.set(cache_key, queryset, 60 * 5)  # 5 минут

        return queryset

    def get_context_data(self, **kwargs):
        # Пагинация работает с обычным списком, нужно вручную нарезать
        context = super().get_context_data(**kwargs)
        # После получения всего списка, пагинация уже выполнена в родительском методе
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница продукта (только для авторизованных)"""
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'
    login_url = '/users/login/'


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание продукта (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = '/users/login/'

    def form_valid(self, form):
        # Автоматически назначаем владельца
        form.instance.owner = self.request.user
        messages.success(self.request, 'Продукт успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Ошибка в поле {field}: {error}')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    login_url = '/users/login/'

    def test_func(self):
        # Только владелец может редактировать
        product = self.get_object()
        return self.request.user == product.owner

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

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


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Удаление продукта: владелец или модератор."""
    login_url = '/users/login/'

    def test_func(self):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        user = self.request.user
        # Владелец или пользователь с правом удаления
        return user == product.owner or user.has_perm('catalog.delete_product')

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.success(request, 'Продукт успешно удален!')
        return redirect('catalog:product_list')


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Отмена публикации продукта (только для модераторов)."""
    login_url = '/users/login/'

    def test_func(self):
        return self.request.user.has_perm('catalog.can_unpublish_product')

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_published = False
        product.save(update_fields=['is_published'])
        messages.success(request, f'Публикация продукта "{product.product_name}" отменена.')
        return redirect('catalog:product_detail', pk=pk)


class ProductsByCategoryView(ListView):
    template_name = 'products_by_category.html'
    context_object_name = 'products'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Проверяем существование категории до выполнения запроса
        self.category = get_object_or_404(Category, pk=kwargs['category_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_products_by_category(self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context