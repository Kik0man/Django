from django.urls import path
from catalog.views import (
    HomeView,
    ContactsView,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView  
)

app_name = "catalog"

urlpatterns = [
    # Главная страница
    path('', HomeView.as_view(), name='home'),
    path('contacts/', ContactsView.as_view(), name='contacts'),

    # CRUD для продуктов
    path('product_list/', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product_add/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),  # Добавляем редактирование
]