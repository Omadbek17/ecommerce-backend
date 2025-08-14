import django_filters
from django.db import models
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """Advanced product filtering"""
    
    # Price range
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name='price')
    
    # Text filters
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='icontains')
    seller_code = django_filters.CharFilter(field_name='seller_code', lookup_expr='iexact')
    
    # Category filters
    category = django_filters.NumberFilter(field_name='category__id')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    
    # Company filter
    company = django_filters.NumberFilter(field_name='company__id')
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    
    # Boolean filters
    in_stock = django_filters.BooleanFilter(field_name='in_stock')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    
    # Date filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Multiple choice filters
    brands = django_filters.CharFilter(method='filter_brands')
    categories = django_filters.CharFilter(method='filter_categories')
    
    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'gte', 'lte'],
            'brand': ['exact', 'icontains'],
            'category': ['exact'],
            'company': ['exact'],
            'in_stock': ['exact'],
            'is_featured': ['exact'],
            'created_at': ['gte', 'lte'],
        }
    
    def filter_brands(self, queryset, name, value):
        """Multiple brands filter: ?brands=bosch,makita,hilti"""
        if not value:
            return queryset
        
        brands_list = [brand.strip() for brand in value.split(',')]
        return queryset.filter(brand__in=brands_list)
    
    def filter_categories(self, queryset, name, value):
        """Multiple categories filter: ?categories=1,2,3"""
        if not value:
            return queryset
        
        try:
            category_ids = [int(cat_id.strip()) for cat_id in value.split(',')]
            return queryset.filter(category__id__in=category_ids)
        except ValueError:
            return queryset