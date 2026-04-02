from django.urls import path
from catalog.views import home, contacts, product_list, product_create, product_detail

app_name = "catalog"

urlpatterns = [
    # path('', home, name='home'),
    # path('contacts/', contacts, name='contacts'),
    path('product_list/', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product_add/', product_create, name='product_create'),
]