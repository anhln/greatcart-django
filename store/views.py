from math import prod
from unicodedata import category
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from cart.views import _cart_id
from category.models import Category
from cart.models import CartItem, Cart
from django.core.paginator import Paginator
from store.models import Product
from django.db.models import Q
from .models import ProductGallery, ReviewRating
from .forms import ReviewForm
from django.contrib import messages
from order.models import OrderProduct



# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug) 
        products = Product.objects.filter(category=categories, is_available = True).order_by('id')
        pageginator = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_obj = pageginator.get_page(page_number)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        pageginator = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_obj = pageginator.get_page(page_number)
        product_count = products.count()
    
    context = {
        'products': page_obj,
        'product_count': product_count,
        'page_obj': page_obj,
    }
    
    return render(request, 'store/store.html', context=context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    # Get Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    # Get the reviews 
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery' :  product_gallery,
        
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) |Q(product_name__icontains=keyword))
        context = {
            'products': products,
            'product_count': products.count,
        }
        return render(request, 'store/store.html', context)
    
    
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            