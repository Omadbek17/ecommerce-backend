# products/admin.py
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
    list_display = ['title', 'seller_code', 'category', 'price', 'in_stock', 'is_active', 'is_featured']
    list_filter = ['in_stock', 'is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'seller_code', 'description', 'brand']
    list_editable = ['price', 'in_stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'seller_code', 'category', 'seller', 'description')
        }),
        ('Narx va Ombor', {
            'fields': ('price', 'in_stock'),
            'description': 'Mahsulot narxi va omborda mavjudligi (✓ = Bor, ✗ = Yo\'q)'
        }),
        ('Mahsulot detallari', {
            'fields': ('brand', 'weight', 'dimensions', 'color', 'material'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [ProductImageInline, ProductSpecificationInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yangi mahsulot yaratilayotganda
            if not obj.seller_id:
                obj.seller = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Admin bo'lmasa faqat o'z mahsulotlarini ko'radi
        if not request.user.is_superuser:
            qs = qs.filter(seller=request.user)
        return qs

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__title', 'alt_text']
    list_editable = ['is_primary', 'order']
    readonly_fields = ['created_at']

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'value', 'order']
    list_filter = ['product']
    search_fields = ['product__title', 'name', 'value']
    list_editable = ['value', 'order']