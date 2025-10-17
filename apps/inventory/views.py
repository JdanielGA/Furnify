# apps/inventory/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category

# List view for categories
class CategoryListView(ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

# Detail view for a single category
class CategoryDetailView(DetailView):
    model = Category
    template_name = 'inventory/category_details.html'
    context_object_name = 'category'