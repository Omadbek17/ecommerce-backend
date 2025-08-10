# products/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Min, Max
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, ProductImage, ProductSpecification
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, 
    ProductImageSerializer, ProductSpecificationSerializer,
    ProductCreateUpdateSerializer
)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Products ViewSet - Read only for customers
    Create/Update/Delete through admin panel
    """
    queryset = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images', 'specifications')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = ['title', 'description', 'seller_code', 'brand']
    
    # Ordering fields
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']  # Default ordering
    
    # Filter fields
    filterset_fields = {
        'category': ['exact'],
        'category__parent': ['exact'],
        'price': ['gte', 'lte', 'exact'],
        'is_featured': ['exact'],
        'in_stock': ['exact'],  # in_stock filter
        'brand': ['exact', 'icontains'],
    }
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filters
        category_id = self.request.query_params.get('category', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        in_stock = self.request.query_params.get('in_stock', None)
        featured = self.request.query_params.get('featured', None)
        
        # Filter by category (including subcategories)
        if category_id:
            # Include products from subcategories too
            from categories.models import Category
            try:
                category = Category.objects.get(id=category_id)
                category_ids = [category.id]
                # Add all descendant categories
                descendants = category.children.filter(is_active=True)
                category_ids.extend([desc.id for desc in descendants])
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                queryset = queryset.filter(category_id=category_id)
        
        # Price range filter
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Stock filter - SODDALASHTIRILGAN
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(in_stock=True)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(in_stock=False)
        
        # Featured filter
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest products"""
        latest_products = self.get_queryset().order_by('-created_at')[:20]
        serializer = ProductListSerializer(latest_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular products (by views or sales - for now just featured)"""
        popular_products = self.get_queryset().filter(is_featured=True).order_by('?')[:15]
        serializer = ProductListSerializer(popular_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get only in-stock products"""
        in_stock_products = self.get_queryset().filter(in_stock=True)
        page = self.paginate_queryset(in_stock_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(in_stock_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out-of-stock products"""
        out_of_stock_products = self.get_queryset().filter(in_stock=False)
        page = self.paginate_queryset(out_of_stock_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(out_of_stock_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Get all images for a product"""
        product = self.get_object()
        images = product.images.all().order_by('order', 'created_at')
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def specifications(self, request, pk=None):
        """Get all specifications for a product"""
        product = self.get_object()
        specs = product.specifications.all().order_by('order')
        serializer = ProductSpecificationSerializer(specs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar products (same category)"""
        product = self.get_object()
        similar_products = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:8]
        
        serializer = ProductListSerializer(similar_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Get available filter options"""
        queryset = self.get_queryset()
        
        # Price range
        price_stats = queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Available brands
        brands = queryset.values_list('brand', flat=True).distinct().exclude(brand='')
        
        # Available categories
        from categories.models import Category
        category_ids = queryset.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=category_ids, is_active=True)
        
        # Stock statistics
        in_stock_count = queryset.filter(in_stock=True).count()
        out_of_stock_count = queryset.filter(in_stock=False).count()
        
        return Response({
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 0)
            },
            'brands': sorted([brand for brand in brands if brand]),
            'categories': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': queryset.filter(category=cat).count()
                }
                for cat in categories
            ],
            'stock': {
                'in_stock': in_stock_count,
                'out_of_stock': out_of_stock_count
            },
            'total_products': queryset.count()
        })
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """Get search suggestions based on query"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        # Search in product titles and brands
        suggestions = []
        
        # Product title suggestions
        products = self.get_queryset().filter(
            Q(title__icontains=query)
        ).values_list('title', flat=True)[:5]
        suggestions.extend([{'text': title, 'type': 'product'} for title in products])
        
        # Brand suggestions  
        brands = self.get_queryset().filter(
            Q(brand__icontains=query)
        ).values_list('brand', flat=True).distinct()[:3]
        suggestions.extend([{'text': brand, 'type': 'brand'} for brand in brands if brand])
        
        return Response(suggestions[:8])
    
    def list(self, request, *args, **kwargs):
        """Override list to add metadata"""
        response = super().list(request, *args, **kwargs)
        
        # Add metadata
        queryset = self.filter_queryset(self.get_queryset())
        
        response.data = {
            'results': response.data,
            'metadata': {
                'total_count': queryset.count(),
                'filters_applied': {
                    'category': request.query_params.get('category'),
                    'search': request.query_params.get('search'),
                    'min_price': request.query_params.get('min_price'),
                    'max_price': request.query_params.get('max_price'),
                    'in_stock': request.query_params.get('in_stock'),
                }
            }
        }
        
        return response