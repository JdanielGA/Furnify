# apps/inventory/urls.py
from django.urls import path
from . import views


app_name = 'inventory'

urlpatterns = [
    # Category URLs
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_details'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
]