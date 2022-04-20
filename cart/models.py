from itertools import product
from django.db import models
from store.models import Product, Variation
from django.contrib import admin

# Create your models here.    
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.quantity * self.product.price
    
    def __unicode__(self) -> str:
        return self.product
    