from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Categories ViewSet - Read only for customers
    Create/Update/Delete through admin panel
    """
    queryset = Category.objects.filter(is_active=True).prefetch_related('children')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter parameters
        parent_only = self.request.query_params.get('parent_only', None)
        parent_id = self.request.query_params.get('parent', None)
        search = self.request.query_params.get('search', None)
        
        # Parent categories only
        if parent_only:
            queryset = queryset.filter(parent=None)
        
        # Children of specific parent
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        # Search by name
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Annotate with product count
        queryset = queryset.annotate(
            total_products=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get subcategories of a specific category"""
        category = self.get_object()
        subcategories = category.children.filter(is_active=True).annotate(
            total_products=Count('products', filter=Q(products__is_active=True))
        )
        serializer = CategoryListSerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in this category (basic info)"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        
        # Basic product info without full serializer to avoid circular import
        product_data = []
        for product in products:
            primary_image = product.images.filter(is_primary=True).first()
            product_data.append({
                'id': product.id,
                'title': product.title,
                'seller_code': product.seller_code,
                'price': str(product.price),
                'is_in_stock': product.is_in_stock,
                'primary_image': request.build_absolute_uri(primary_image.image.url) if primary_image else None,
                'created_at': product.created_at
            })
        
        return Response({
            'category': CategorySerializer(category, context={'request': request}).data,
            'products': product_data,
            'count': len(product_data)
        })
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get full category tree structure"""
        # Get all parent categories with their children
        parent_categories = self.get_queryset().filter(parent=None)
        
        tree_data = []
        for parent in parent_categories:
            children = parent.children.filter(is_active=True).annotate(
                total_products=Count('products', filter=Q(products__is_active=True))
            )
            
            parent_data = CategorySerializer(parent, context={'request': request}).data
            parent_data['children'] = CategoryListSerializer(children, many=True, context={'request': request}).data
            tree_data.append(parent_data)
        
        return Response(tree_data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular categories (by product count)"""
        popular_categories = self.get_queryset().annotate(
            total_products=Count('products', filter=Q(products__is_active=True))
        ).filter(total_products__gt=0).order_by('-total_products')[:10]
        
        serializer = CategoryListSerializer(popular_categories, many=True, context={'request': request})
        return Response(serializer.data)