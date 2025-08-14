# products/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Min, Max
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Product, ProductImage, ProductSpecification
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, 
    ProductImageSerializer, ProductSpecificationSerializer,
    ProductCreateUpdateSerializer
)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Products ViewSet - Advanced search and filtering
    Mahsulotlar API - Kengaytirilgan qidiruv va filterlash bilan
    """
    queryset = Product.objects.filter(is_active=True).select_related(
        'category', 'seller', 'company'
    ).prefetch_related('images', 'specifications')
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
        'company': ['exact'],
        'price': ['gte', 'lte', 'exact'],
        'is_featured': ['exact'],
        'in_stock': ['exact'],
        'brand': ['exact', 'icontains'],
    }
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filters from query params
        category_id = self.request.query_params.get('category', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        in_stock = self.request.query_params.get('in_stock', None)
        featured = self.request.query_params.get('featured', None)
        company_id = self.request.query_params.get('company', None)
        brand = self.request.query_params.get('brand', None)
        
        # Filter by company
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by category (including subcategories)
        if category_id:
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
        
        # Stock filter
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(in_stock=True)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(in_stock=False)
        
        # Featured filter
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Brand filter
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        return queryset
    
    @extend_schema(
        summary="Barcha mahsulotlar ro'yxati",
        description="Mahsulotlar ro'yxati kengaytirilgan filter va qidiruv imkoniyatlari bilan",
        parameters=[
            OpenApiParameter(name='search', description='Qidiruv so\'zi', type=OpenApiTypes.STR),
            OpenApiParameter(name='category', description='Kategoriya ID', type=OpenApiTypes.INT),
            OpenApiParameter(name='company', description='Kompaniya ID', type=OpenApiTypes.INT),
            OpenApiParameter(name='min_price', description='Minimal narx', type=OpenApiTypes.NUMBER),
            OpenApiParameter(name='max_price', description='Maksimal narx', type=OpenApiTypes.NUMBER),
            OpenApiParameter(name='brand', description='Brend nomi', type=OpenApiTypes.STR),
            OpenApiParameter(name='in_stock', description='Omborda bor (true/false)', type=OpenApiTypes.BOOL),
            OpenApiParameter(name='featured', description='Tavsiya etilgan (true/false)', type=OpenApiTypes.BOOL),
            OpenApiParameter(name='ordering', description='Saralash: price, -price, created_at, -created_at, title', type=OpenApiTypes.STR),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Enhanced list with metadata"""
        response = super().list(request, *args, **kwargs)
        
        # Add metadata
        queryset = self.filter_queryset(self.get_queryset())
        
        if hasattr(response, 'data') and isinstance(response.data, dict):
            response.data['metadata'] = {
                'total_count': queryset.count(),
                'filters_applied': {
                    'category': request.query_params.get('category'),
                    'company': request.query_params.get('company'),
                    'search': request.query_params.get('search'),
                    'min_price': request.query_params.get('min_price'),
                    'max_price': request.query_params.get('max_price'),
                    'in_stock': request.query_params.get('in_stock'),
                    'brand': request.query_params.get('brand'),
                }
            }
        
        return response
    
    @extend_schema(
        summary="Mahsulotlarni qidirish",
        description="Mahsulot nomi, tavsifi, brend, kodi bo'yicha qidiruv",
        parameters=[
            OpenApiParameter(name='q', description='Qidiruv so\'zi (majburiy)', type=OpenApiTypes.STR, required=True),
            OpenApiParameter(name='category', description='Kategoriya ID', type=OpenApiTypes.INT),
            OpenApiParameter(name='company', description='Kompaniya ID', type=OpenApiTypes.INT),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Enhanced search functionality"""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({
                'error': 'Qidiruv so\'zi kiritilmagan',
                'message': 'q parametri majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Base queryset
        queryset = self.get_queryset()
        
        # Search across multiple fields
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(seller_code__icontains=query)
        )
        
        # Optional filters
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        company_id = request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
            'query': query
        })
    
    @extend_schema(summary="Tavsiya etilgan mahsulotlar")
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response({
            'count': len(featured_products),
            'results': serializer.data
        })
    
    @extend_schema(summary="Eng yangi mahsulotlar")
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest products"""
        limit = int(request.query_params.get('limit', 20))
        latest_products = self.get_queryset().order_by('-created_at')[:limit]
        serializer = ProductListSerializer(latest_products, many=True, context={'request': request})
        return Response({
            'count': len(latest_products),
            'results': serializer.data
        })
    
    @extend_schema(summary="Mashhur mahsulotlar")
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular products"""
        popular_products = self.get_queryset().filter(is_featured=True).order_by('?')[:15]
        serializer = ProductListSerializer(popular_products, many=True, context={'request': request})
        return Response({
            'count': len(popular_products),
            'results': serializer.data
        })
    
    @extend_schema(summary="Omborda mavjud mahsulotlar")
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
    
    @extend_schema(summary="O'xshash mahsulotlar")
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related/similar products"""
        product = self.get_object()
        
        # Same category products, excluding current product
        queryset = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)
        
        # Prioritize same brand
        same_brand = queryset.filter(brand=product.brand)
        if same_brand.exists():
            queryset = same_brand
        
        # Limit to 8 products
        related_products = queryset[:8]
        
        serializer = ProductListSerializer(related_products, many=True, context={'request': request})
        return Response({
            'count': len(related_products),
            'results': serializer.data
        })
    
    @extend_schema(summary="Filter imkoniyatlari")
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
        
        # Available companies
        from companies.models import Company
        company_ids = queryset.values_list('company_id', flat=True).distinct()
        companies = Company.objects.filter(id__in=company_ids, is_active=True)
        
        # Available categories
        from categories.models import Category
        category_ids = queryset.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=category_ids, is_active=True)
        
        return Response({
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 0)
            },
            'brands': sorted([brand for brand in brands if brand]),
            'companies': [
                {
                    'id': comp.id,
                    'name': comp.name,
                    'product_count': queryset.filter(company=comp).count()
                }
                for comp in companies
            ],
            'categories': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': queryset.filter(category=cat).count()
                }
                for cat in categories
            ],
            'stock': {
                'in_stock': queryset.filter(in_stock=True).count(),
                'out_of_stock': queryset.filter(in_stock=False).count()
            },
            'total_products': queryset.count()
        })
    
    # Sizning mavjud methodlaringiz...
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
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        suggestions = []
        
        # Product suggestions
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