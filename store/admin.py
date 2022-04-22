from django.contrib import admin
import admin_thumbnails


from store.models import Product, ProductGallery, ReviewRating, Variation

# Register your models here.

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category', 'variation_value', 'is_active', 'created_date')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category', 'variation_value', 'created_date')
    
admin.site.register(ReviewRating)    
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductGallery)
