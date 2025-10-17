# apps/inventory/urls.py
from django.urls import path
from .views import CategoryListView, CategoryDetailView


app_name = 'inventory'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_details'),
]