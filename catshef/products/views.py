from django.shortcuts import render
from products.models import Product, Category
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from common.decorators import ajax_required

def index(request):
    products = Product.objects.all()
    return render(request, 'products/index.html', {
        'products': products,
        })

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    return render(request, 'products/detail.html', {'product': product})

def category(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(categories=category)
    paginator = Paginator(products, 8)
    page_num = request.GET.get('page')
    try:
        products = paginator.page(page_num)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        products = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'products/list_ajax.html', {'products':products,
            'page_num':page_num})
    return render(request, 'products/category_list.html', {'category':category})

@ajax_required
def product_related(request, slug):
    product = Product.active.get(slug=slug)
    products = product.similar_products()
    paginator = Paginator(products, 8)
    page_num = request.GET.get('page')

    try:
        products = paginator.page(page_num)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        return HttpResponse('')
    return render(request, 'products/list_ajax.html', {'products':products})
