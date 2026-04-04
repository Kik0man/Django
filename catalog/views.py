from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

def contacts(request):
    return render(request, 'contacts.html')

def product_list(request):
    products = Product.objects.all().order_by('id')
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product_list.html', {'page_obj': page_obj})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog:product_list')  # 👈 ДОБАВЬТЕ 'catalog:'
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})
