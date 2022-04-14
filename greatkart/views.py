from multiprocessing import context
from django.shortcuts import get_object_or_404, render

from store.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)