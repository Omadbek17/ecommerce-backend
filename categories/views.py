from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Min, Max, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Categories ViewSet - Enhanced with advanced features
    Kategoriyalar API - Kengaytirilgan imkoniyatlar bilan
    """
    queryset = Category.objects.filter(is_active=True).prefetch_related('children', 'products')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    filterset_fields = {
        'parent': ['exact', 'isnull'],
        'company': ['exact'],
    }
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategorySerializer
        return CategoryListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filters
        parent_only = self.request.query_params.get('parent_only', None)
        parent_id = self.request.query_params.get('parent', None)
        company_id = self.request.query_params.get('company', None)
        has_products = self.request.query_params.get('has_products', None)
        search = self.request.query_params.get('search', None)
        
        # Filter by company
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Parent categories only
        if parent_only and parent_only.lower() == 'true':
            queryset = queryset.filter(parent=None)
        
        # Children of specific parent
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        # Categories with products
        if has_products and has_products.lower() == 'true':
            queryset = queryset.filter(products__isnull=False).distinct()
        
        # Search by name or description
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Always annotate with product count
        queryset = queryset.annotate(
            total_products=Count('products', filter=Q(products__is_active=True))
        )
        
        return queryset
    
    @extend_schema(
        summary="Barcha kategoriyalar ro'yxati",
        description="Kategoriyalar ro'yxati kengaytirilgan filter imkoniyatlari bilan",
        parameters=[
            OpenApiParameter(name='search', description='Kategoriya nomi bo\'yicha qidiruv', type=OpenApiTypes.STR),
            OpenApiParameter(name='company', description='Kompaniya ID', type=OpenApiTypes.INT),
            OpenApiParameter(name='parent', description='Parent kategoriya ID', type=OpenApiTypes.INT),
            OpenApiParameter(name='parent_only', description='Faqat asosiy kategoriyalar (true/false)', type=OpenApiTypes.BOOL),
            OpenApiParameter(name='has_products', description='Mahsuloti bor kategoriyalar (true/false)', type=OpenApiTypes.BOOL),
            OpenApiParameter(name='ordering', description='Saralash: order, name, -created_at', type=OpenApiTypes.STR),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Kategoriya detallari",
        description="Bitta kategoriya haqida to'liq ma'lumot"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Kategoriyalar ierarxiyasi",
        description="Barcha kategoriyalar to'liq ierarxiya ko'rinishida",
        parameters=[
            OpenApiParameter(name='company', description='Kompaniya ID', type=OpenApiTypes.INT),
        ]
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get full category tree structure - Enhanced"""
        company_id = request.query_params.get('company')
        
        # Get parent categories
        parent_categories = self.get_queryset().filter(parent=None)
        if company_id:
            parent_categories = parent_categories.filter(company_id=company_id)
        
        tree_data = []
        for parent in parent_categories:
            children = parent.children.filter(is_active=True).annotate(
                total_products=Count('products', filter=Q(products__is_active=True))
            )
            
            parent_data = CategorySerializer(parent, context={'request': request}).data
            parent_data['children'] = CategoryListSerializer(children, many=True, context={'request': request}).data
            parent_data['total_children'] = children.count()
            tree_data.append(parent_data)
        
        return Response({
            'count': len(tree_data),
            'tree': tree_data
        })
    
    @extend_schema(
        summary="Asosiy kategoriyalar",
        description="Faqat asosiy (parent=None) kategoriyalar"
    )
    @action(detail=False, methods=['get'])
    def root(self, request):
        """Get root categories only"""
        root_categories = self.get_queryset().filter(parent=None)
        serializer = CategoryListSerializer(root_categories, many=True, context={'request': request})
        return Response({
            'count': root_categories.count(),
            'results': serializer.data
        })
    
    @extend_schema(
        summary="Mashhur kategoriyalar",
        description="Eng ko'p mahsulotga ega kategoriyalar",
        parameters=[
            OpenApiParameter(name='limit', description='Cheklash (default: 10)', type=OpenApiTypes.INT),
        ]
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular categories by product count - Enhanced"""
        limit = int(request.query_params.get('limit', 10))
        
        popular_categories = self.get_queryset().filter(
            total_products__gt=0
        ).order_by('-total_products')[:limit]
        
        serializer = CategoryListSerializer(popular_categories, many=True, context={'request': request})
        return Response({
            'count': len(popular_categories),
            'results': serializer.data
        })
    
    @extend_schema(
        summary="Kategoriya sublari",
        description="Tanlangan kategoriyaning barcha subkategoriyalari"
    )
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get subcategories of a specific category - Enhanced"""
        category = self.get_object()
        subcategories = category.children.filter(is_active=True).annotate(
            total_products=Count('products', filter=Q(products__is_active=True))
        )
        
        serializer = CategoryListSerializer(subcategories, many=True, context={'request': request})
        return Response({
            'parent': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            },
            'count': subcategories.count(),
            'subcategories': serializer.data
        })
    
    @extend_schema(
        summary="Kategoriya mahsulotlari",
        description="Tanlangan kategoriyaning barcha mahsulotlari",
        parameters=[
            OpenApiParameter(name='include_subcategories', description='Subkategoriya mahsulotlari ham (true/false)', type=OpenApiTypes.BOOL),
            OpenApiParameter(name='ordering', description='Saralash: price, -price, created_at', type=OpenApiTypes.STR),
            OpenApiParameter(name='limit', description='Cheklash', type=OpenApiTypes.INT),
        ]
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in this category - Enhanced"""
        category = self.get_object()
        include_subcategories = request.query_params.get('include_subcategories', 'false').lower() == 'true'
        ordering = request.query_params.get('ordering', '-created_at')
        limit = request.query_params.get('limit')
        
        if include_subcategories:
            # Include products from subcategories
            category_ids = [category.id]
            subcategories = category.children.filter(is_active=True)
            category_ids.extend([sub.id for sub in subcategories])
            products = category.products.model.objects.filter(
                category_id__in=category_ids,
                is_active=True
            )
        else:
            products = category.products.filter(is_active=True)
        
        # Ordering
        if ordering in ['price', '-price', 'created_at', '-created_at', 'title', '-title']:
            products = products.order_by(ordering)
        
        # Limit
        if limit:
            try:
                products = products[:int(limit)]
            except ValueError:
                pass
        
        # Build product data to avoid circular import
        product_data = []
        for product in products:
            primary_image = product.images.filter(is_primary=True).first()
            product_data.append({
                'id': product.id,
                'title': product.title,
                'seller_code': product.seller_code,
                'price': str(product.price),
                'brand': product.brand,
                'in_stock': product.in_stock,
                'is_featured': product.is_featured,
                'primary_image': request.build_absolute_uri(primary_image.image.url) if primary_image else None,
                'seller_name': product.seller.get_full_name() if hasattr(product.seller, 'get_full_name') else str(product.seller),
                'created_at': product.created_at
            })
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            },
            'include_subcategories': include_subcategories,
            'count': len(product_data),
            'products': product_data
        })
    
    @extend_schema(
        summary="Kategoriya statistikasi",
        description="Kategoriya bo'yicha statistik ma'lumotlar"
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get category statistics"""
        category = self.get_object()
        
        # Direct products
        direct_products = category.products.filter(is_active=True)
        direct_count = direct_products.count()
        
        # Subcategories count
        subcategories_count = category.children.filter(is_active=True).count()
        
        # Price statistics for direct products
        price_stats = direct_products.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )
        
        # Stock statistics
        in_stock_count = direct_products.filter(in_stock=True).count()
        out_of_stock_count = direct_products.filter(in_stock=False).count()
        
        # Brand statistics
        brands = direct_products.values_list('brand', flat=True).distinct().exclude(brand='')
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            },
            'products': {
                'total': direct_count,
                'in_stock': in_stock_count,
                'out_of_stock': out_of_stock_count
            },
            'subcategories_count': subcategories_count,
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 0),
                'average': float(price_stats['avg_price'] or 0)
            },
            'brands': {
                'count': len(brands),
                'list': sorted([brand for brand in brands if brand])
            }
        })
    
    @extend_schema(
        summary="Bo'sh kategoriyalar",
        description="Mahsuloti yo'q kategoriyalar"
    )
    @action(detail=False, methods=['get'])
    def empty(self, request):
        """Get categories without products"""
        empty_categories = self.get_queryset().filter(total_products=0)
        serializer = CategoryListSerializer(empty_categories, many=True, context={'request': request})
        return Response({
            'count': empty_categories.count(),
            'results': serializer.data
        })
    
    @extend_schema(
        summary="Kategoriya qidiruv tavsiyalari",
        description="Kategoriya nomlari bo'yicha qidiruv tavsiyalari",
        parameters=[
            OpenApiParameter(name='q', description='Qidiruv so\'zi', type=OpenApiTypes.STR, required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """Get category search suggestions"""
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response([])
        
        suggestions = self.get_queryset().filter(
            Q(name__icontains=query)
        ).values('id', 'name').annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )[:8]
        
        return Response([
            {
                'id': item['id'],
                'name': item['name'],
                'product_count': item['product_count'],
                'type': 'category'
            }
            for item in suggestions
        ])
    
    @extend_schema(
        summary="Kategoriyalar filterlari",
        description="Mavjud filter imkoniyatlari"
    )
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Get available category filters"""
        queryset = self.get_queryset()
        
        # Companies with categories
        from companies.models import Company
        company_ids = queryset.values_list('company_id', flat=True).distinct()
        companies = Company.objects.filter(id__in=company_ids, is_active=True)
        
        # Category statistics
        total_categories = queryset.count()
        root_categories = queryset.filter(parent=None).count()
        categories_with_products = queryset.filter(total_products__gt=0).count()
        empty_categories = queryset.filter(total_products=0).count()
        
        return Response({
            'companies': [
                {
                    'id': comp.id,
                    'name': comp.name,
                    'category_count': queryset.filter(company=comp).count()
                }
                for comp in companies
            ],
            'statistics': {
                'total_categories': total_categories,
                'root_categories': root_categories,
                'categories_with_products': categories_with_products,
                'empty_categories': empty_categories
            }
        })