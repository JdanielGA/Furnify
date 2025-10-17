# apps/inventory/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'parent') # Display hierarchy, slug, and parent in admin list view.
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)} # Auto-fill slug from name.
