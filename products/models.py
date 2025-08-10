from django.db import models
from django.contrib.auth import get_user_model
from categories.models import Category

User = get_user_model()

class Product(models.Model):
    title = models.CharField(max_length=200)
    seller_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    # SODDA OMBOR - faqat bor yoki yo'q
    in_stock = models.BooleanField(default=True, verbose_name="Omborda bormi")
    
    # Product details
    brand = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text="Og'irligi (kg)")
    dimensions = models.CharField(max_length=100, blank=True, help_text="Uzunlik x Kenglik x Balandlik")
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
    
    def __str__(self):
        return f"{self.title} - {self.seller_code}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.product.title} - Rasm {self.order}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.title} - {self.name}: {self.value}"