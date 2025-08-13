from rest_framework import serializers
from .models import Company
from drf_spectacular.utils import extend_schema_field

class CompanyListSerializer(serializers.ModelSerializer):
    """Kompaniyalar ro'yxati uchun serializer"""
    categories_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo', 'logo_url', 'slug', 'categories_count', 'products_count']
    
    @extend_schema_field(serializers.IntegerField)
    def get_categories_count(self, obj):
        """Kompaniyaning kategoriyalar soni"""
        try:
            # Agar Category model Company ga bog'langan bo'lsa
            from categories.models import Category
            return Category.objects.filter(company=obj, is_active=True, parent=None).count()
        except:
            return 0
    
    @extend_schema_field(serializers.IntegerField)
    def get_products_count(self, obj):
        """Kompaniyaning mahsulotlar soni"""
        try:
            # Agar Product model Company ga bog'langan bo'lsa
            from products.models import Product
            return Product.objects.filter(company=obj, is_active=True).count()
        except:
            return 0
    
    @extend_schema_field(serializers.CharField)
    def get_logo_url(self, obj):
        """Logo URL (to'liq)"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

class CompanyDetailSerializer(serializers.ModelSerializer):
    """Kompaniya detallari uchun serializer"""
    categories = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo', 'logo_url', 'description', 'slug', 'categories', 'created_at']
    
    @extend_schema_field(serializers.ListField)
    def get_categories(self, obj):
        """Kompaniyaning barcha kategoriyalari"""
        try:
            from categories.models import Category
            from categories.serializers import CategoryListSerializer
            categories = Category.objects.filter(company=obj, parent=None, is_active=True)
            return CategoryListSerializer(categories, many=True, context=self.context).data
        except:
            return []
    
    @extend_schema_field(serializers.CharField)
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
        return None