from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller_code', 'price', 'category', 'seller', 'stock_quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'seller_code', 'description')
    ordering = ('-created_at',)
    list_editable = ('price', 'stock_quantity', 'is_active')
    inlines = [ProductImageInline, ProductSpecificationInline]