# apps/inventory/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category, Product
from .forms import CategoryForm
from django.urls import reverse_lazy

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

# Create view for adding a new category
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

# Update view for editing an existing category
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

# Delete view for removing a category
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')

# # apps/inventory/views.py (Product views)
# List view for products.
class ProductListView(ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.select_related('category')