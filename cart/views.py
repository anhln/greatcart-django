from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    '''get SessionId'''
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

    
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
            
    
    # get Cart or create Cart
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart(
            cart_id = _cart_id(request)
        )
        cart.save()

    # get CartItem or create CartItem or update CartItem
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(cart = cart, product=product)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
            
        if product_variation in ex_var_list:
            # increase the cart item quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()   
            
    else:
        cart_item = CartItem.objects.create(
            cart = cart,
            product = product,
            quantity = 1
        )
        if len(product_variation) > 0:
            # cart_item.variations.clear()
            # for item in product_variation:
            cart_item.variations.add(*product_variation)
                
        cart_item.save()
    return redirect('cart')
    
    
def remove_cart(request, product_id, cart_item_id):
    # get Cart or create Cart
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart = cart, product=product, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    # get Cart or create Cart
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart = cart, product=product, id=cart_item_id)
    cart_item.delete()
    
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            total = total + cart_item.quantity * cart_item.product.price
            quantity = quantity + cart_item.quantity
        tax = 0.02 * total
        grand_total = tax + total
        
    except ObjectDoesNotExist:
        pass #just ignore
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    
    return render(request, 'cart.html', context=context)