# apps/inventory/forms.py
from django import forms
from .models import Category

# Form for creating and updating Category instances.
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }