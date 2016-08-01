from django.shortcuts import render
from products.models import Product

def index(request):
    products = Product.objects.all()
    return render(request, 'products/index.html', {
        'products': products,
        })

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    return render(request, 'products/detail.html', {'product': product})
