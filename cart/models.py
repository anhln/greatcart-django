from itertools import product
from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from django.contrib import admin

# Create your models here.    

class CartItemManager(models.Manager):
    def get_total_price_quantity(self, current_user=None, cart=None ):
        if current_user is not None:
            cart_items = self.filter(user=current_user)
        else:
            cart_items = self.filter(cart=cart, is_active=True)
        total = 0
        quantity = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        return [total, quantity]
        
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    objects = CartItemManager()
    
    def sub_total(self):
        return self.quantity * self.product.price
    
    def __unicode__(self) -> str:
        return self.product
    