from rest_framework import serializers
from .models import Category

class CategoryListSerializer(serializers.ModelSerializer):
    """Simple category serializer for lists"""
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'image_url', 'product_count', 'parent')
    
    def get_product_count(self, obj):
        # Use annotated value if available, otherwise calculate
        if hasattr(obj, 'total_products'):
            return obj.total_products
        return obj.products.filter(is_active=True).count()
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CategorySerializer(serializers.ModelSerializer):
    """Detailed category serializer"""
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    breadcrumbs = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'image_url', 'parent', 'parent_name',
            'product_count', 'children', 'breadcrumbs', 'is_active', 
            'created_at', 'updated_at'
        )
    
    def get_product_count(self, obj):
        # Include products from child categories
        if hasattr(obj, 'total_products'):
            return obj.total_products
        
        # Direct products
        direct_count = obj.products.filter(is_active=True).count()
        
        # Products from child categories
        child_count = 0
        for child in obj.children.filter(is_active=True):
            child_count += child.products.filter(is_active=True).count()
        
        return direct_count + child_count
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_children(self, obj):
        # Only return active children
        children = obj.children.filter(is_active=True)
        if children.exists():
            return CategoryListSerializer(children, many=True, context=self.context).data
        return []
    
    def get_breadcrumbs(self, obj):
        """Generate breadcrumb trail"""
        breadcrumbs = []
        current = obj
        
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'name': current.name
            })
            current = current.parent
        
        return breadcrumbs


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating categories (admin only)"""
    
    class Meta:
        model = Category
        fields = ('name', 'description', 'image', 'parent', 'is_active')
    
    def validate(self, attrs):
        # Prevent circular parent relationships
        parent = attrs.get('parent')
        if parent and self.instance:
            if parent.id == self.instance.id:
                raise serializers.ValidationError("Category cannot be parent of itself")
            
            # Check if parent is a descendant of current category
            current_parent = parent.parent
            while current_parent:
                if current_parent.id == self.instance.id:
                    raise serializers.ValidationError("Cannot create circular parent relationship")
                current_parent = current_parent.parent
        
        return attrs