from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'slug', 'logo', 'description')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )