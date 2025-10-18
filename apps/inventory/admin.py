# apps/inventory/admin.py
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'parent') # Display hierarchy, slug, and parent in admin list view.
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'price', 'stock')
    search_fields = ('name', 'description')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug field based on name.