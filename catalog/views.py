from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from catalog.models import Product
from catalog.forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = "catalog/index.html"
    context_object_name = "products"
    paginate_by = 3


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("home")


def home(request):
    return render(request, "home.html")


def contacts(request):
    return render(request, "contacts.html")
