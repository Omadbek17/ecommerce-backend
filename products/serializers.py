# products/serializers.py
from rest_framework import serializers
from .models import Product, ProductImage, ProductSpecification
from categories.serializers import CategoryListSerializer

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image_url', 'alt_text', 'is_primary', 'order')
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'name', 'value', 'order')


class ProductListSerializer(serializers.ModelSerializer):
    """Simple product serializer for lists"""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'seller_code', 'price', 'primary_image', 
            'category_name', 'seller_name', 'is_in_stock', 'is_low_stock',
            'is_featured', 'brand', 'created_at'
        )
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        # Fallback to first image
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None
    
    def get_seller_name(self, obj):
        return f"{obj.seller.first_name} {obj.seller.last_name}"


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer"""
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    category = CategoryListSerializer(read_only=True)
    seller_name = serializers.SerializerMethodField()
    seller_phone = serializers.CharField(source='seller.phone_number', read_only=True)
    primary_image = serializers.SerializerMethodField()
    all_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'seller_code', 'description', 'price', 
            'category', 'seller_name', 'seller_phone',
            'stock_quantity', 'is_in_stock', 'is_low_stock', 'min_stock_level',
            'brand', 'weight', 'dimensions', 'color', 'material',
            'primary_image', 'all_images', 'images', 'specifications',
            'is_featured', 'created_at', 'updated_at'
        )
    
    def get_seller_name(self, obj):
        return f"{obj.seller.first_name} {obj.seller.last_name}"
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_all_images(self, obj):
        """Get all product images in order"""
        images = obj.images.all().order_by('order', 'created_at')
        return ProductImageSerializer(images, many=True, context=self.context).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products (admin only)"""
    class Meta:
        model = Product
        fields = (
            'title', 'seller_code', 'description', 'price', 'category',
            'stock_quantity', 'min_stock_level', 'brand', 'weight',
            'dimensions', 'color', 'material', 'meta_title', 'meta_description',
            'is_featured'
        )
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_seller_code(self, value):
        """Ensure seller_code is unique"""
        if self.instance and self.instance.seller_code == value:
            return value
        
        if Product.objects.filter(seller_code=value).exists():
            raise serializers.ValidationError("Bu sotuvchi kodi allaqachon mavjud.")
        return value