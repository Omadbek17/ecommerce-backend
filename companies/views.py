from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Company
from .serializers import CompanyListSerializer, CompanyDetailSerializer

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kompaniyalar API
    
    Barcha kompaniyalar ro'yxati va ularning kategoriyalari/mahsulotlari
    """
    queryset = Company.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanyListSerializer
    
    @extend_schema(
        summary="Barcha kompaniyalar ro'yxati",
        description="Faol kompaniyalar ro'yxatini qaytaradi (EPA, Number One, RODEX, PID va h.k.)",
        responses={200: CompanyListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Kompaniya detallari",
        description="Bitta kompaniya haqida to'liq ma'lumot",
        responses={200: CompanyDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Kompaniya kategoriyalari",
        description="Tanlangan kompaniyaning barcha kategoriyalari",
        responses={200: 'Kategoriyalar ro\'yxati'}
    )
    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """Kompaniyaning kategoriyalarini olish"""
        company = self.get_object()
        categories = company.categories.filter(parent=None, is_active=True).order_by('order', 'name')
        
        from categories.serializers import CategoryListSerializer
        serializer = CategoryListSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Kompaniya mahsulotlari",
        description="Tanlangan kompaniyaning barcha mahsulotlari",
        parameters=[
            OpenApiParameter(name='category', description='Kategoriya ID', type=int),
            OpenApiParameter(name='search', description='Qidiruv', type=str),
            OpenApiParameter(name='min_price', description='Minimal narx', type=int),
            OpenApiParameter(name='max_price', description='Maksimal narx', type=int),
        ],
        responses={200: 'Mahsulotlar ro\'yxati'}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Kompaniyaning mahsulotlarini olish"""
        company = self.get_object()
        products = company.products.filter(is_active=True)
        
        # Filters
        category_id = request.query_params.get('category')
        if category_id:
            products = products.filter(category_id=category_id)
        
        search = request.query_params.get('search')
        if search:
            products = products.filter(title__icontains=search)
        
        min_price = request.query_params.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = request.query_params.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Pagination
        page = self.paginate_queryset(products)
        if page is not None:
            from products.serializers import ProductListSerializer
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        from products.serializers import ProductListSerializer
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)