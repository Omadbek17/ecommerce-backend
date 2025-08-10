from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['name', 'value', 'order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller_code', 'category', 'price', 'in_stock', 'is_active']
    list_filter = ['in_stock', 'is_active', 'is_featured', 'category']
    search_fields = ['title', 'seller_code', 'description']
    list_editable = ['price', 'in_stock', 'is_active']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'seller_code', 'category', 'seller', 'description')
        }),
        ('Narx va Holat', {
            'fields': ('price', 'in_stock')
        }),
        ('Qo\'shimcha', {
            'fields': ('brand', 'weight', 'dimensions', 'color', 'material'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured'),
        }),
    )
    
    inlines = [ProductImageInline, ProductSpecificationInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yangi mahsulot
            obj.seller = request.user
        super().save_model(request, obj, form, change)