from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
)

app_name = CatalogConfig.name

urlpatterns = [
    path("", ProductListView.as_view(), name="home"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("add/", ProductCreateView.as_view(), name="product_add"),
]
