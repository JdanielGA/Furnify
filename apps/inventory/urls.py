# apps/inventory/urls.py
from django.urls import path
from .views import CategoryListView, CategoryDetailView, CategoryCreateView


app_name = 'inventory'

urlpatterns = [
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_details'),
]