# apps/inventory/urls.py
from django.urls import path
from . import views


app_name = 'inventory'

urlpatterns = [
    # Root URL
    path('', views.InventoryHomeView.as_view(), name='inventory_home'),

    # Category URLs
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_details'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Product URLs
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_details'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]