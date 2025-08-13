from django.db import models

class Company(models.Model):
    """Kompaniyalar modeli (EPA, Number One, RODEX, PID)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Kompaniya nomi")
    logo = models.ImageField(upload_to='companies/', blank=True, null=True, verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    slug = models.SlugField(unique=True, verbose_name="URL slug")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqt")  # Bu field qo'shildi
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Kompaniya'
        verbose_name_plural = 'Kompaniyalar'
    
    def __str__(self):
        return self.name