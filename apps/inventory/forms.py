# apps/inventory/forms.py
from django import forms
from .models import Category, Product

# Form for creating and updating Category instances.
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


# Form for creating and updating Product instances.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock