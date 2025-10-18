# apps/inventory/models.py

# Allows using type annotations before they are fully defined.
# Essential for the `parent: Category | None` below.
from __future__ import annotations

import datetime  # Required for the date field type hints.
from django.db import models
from django.utils.text import slugify  # Django function to create slugs.
from django.urls import reverse  # Tool to generate URLs dynamically.

class Category(models.Model):
    """
    Represents a product category.
    Categories can be nested to create a hierarchy.
    """
    # Modern Python type hint for code clarity.
    name: str = models.CharField(
        'name',
        max_length=100,
        unique=True,
        help_text="Name of the category (must be unique)."
    )
    slug: str = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier for SEO (must be unique)."
    )
    description: str = models.TextField(
        'description',
        blank=True, # The field is optional in forms.
        help_text="Detailed description of the category."
    )
    # --- NEW CONCEPT: Hierarchical Relationship ---
    # A ForeignKey to 'self' creates a relationship with the same model.
    parent: Category | None = models.ForeignKey(
        'self',
        verbose_name='parent category',
        null=True,     # Allows the value in the database to be NULL (for root categories).
        blank=True,    # Allows the field to be empty in forms.
        related_name='children', # Allows accessing subcategories with `category.children.all()`.
        on_delete=models.PROTECT, # NEW CONCEPT: Prevents deletion if it has children.
        help_text="Parent category to which this subcategory belongs."
    )
    # Timestamps for auditing.
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)

    class Meta:
        # Names for the Django admin panel.
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        # Default order when querying categories.
        ordering = ['name']

    def __str__(self) -> str:
        """
        Text representation of the object. Displays the full hierarchy.
        Example: 'Home > Furniture > Chairs'
        """
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

    # --- NEW CONCEPT: Canonical URL ---
    def get_absolute_url(self) -> str:
        """
        Returns the unique and permanent URL for this object.
        Used by Django in the admin and by us in templates.
        """
        # 'inventory:category_details' must match the app_name and the name of a URL.
        return reverse('inventory:category_details', kwargs={'slug': self.slug})

    # --- NEW CONCEPT: Custom Business Logic on Save ---
    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to generate a unique and safe slug.
        """
        # 1. Generate a slug from the name if it does not exist.
        if not self.slug:
            self.slug = slugify(self.name)
        
        # 2. Ensure the slug is unique across the entire table.
        #    This logic runs on both creation and update.
        queryset = Category.objects.filter(slug=self.slug)
        
        # 3. If we are updating (the object already has a primary key),
        #    we exclude the object itself from the duplicate check.
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        # 4. If an object with this slug still exists, it is a genuine duplicate.
        if queryset.exists():
            # Save the original slug to use it as a base.
            original_slug = self.slug
            counter = 1
            # Enter a loop until an available slug is found.
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        
        # Call the parent's original `save` method to save the object to the database.
        super().save(*args, **kwargs)

class Product(models.Model):
    """
    Represents a product in the inventory.
    Each product belongs to a category.
    """
    name: str = models.CharField(
        'name',
        max_length=200,
        help_text="Name of the product."
    )
    slug: str = models.SlugField(
        'slug',
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier for SEO (must be unique)."
    )
    category: Category = models.ForeignKey(
        Category,
        verbose_name='category',
        on_delete=models.PROTECT,
        related_name='products',
        help_text="Category to which this product belongs."
    )
    description: str = models.TextField(
        'description',
        blank=True,
        help_text="Detailed description of the product."
    )
    price: float = models.DecimalField(
        'price',
        max_digits=10,
        decimal_places=2,
        help_text="Price of the product."
    )
    photo: str = models.ImageField(
        'photo',
        upload_to='products/',
        blank=True,
        help_text="Image of the product."
    )
    stock: int = models.PositiveIntegerField(
        'stock',
        default=0,
        help_text="Current stock level of the product."
    )

    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse('inventory:product_details', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to generate a unique and safe slug.
        """
        # 1. Generate a slug from the name if it does not exist.
        if not self.slug:
            self.slug = slugify(self.name)
        
        # 2. Ensure the slug is unique across the entire table.
        #    This logic runs on both creation and update.
        queryset = Product.objects.filter(slug=self.slug)
        
        # 3. If we are updating (the object already has a primary key),
        #    we exclude the object itself from the duplicate check.
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        # 4. If an object with this slug still exists, it is a genuine duplicate.
        if queryset.exists():
            # Save the original slug to use it as a base.
            original_slug = self.slug
            counter = 1
            # Enter a loop until an available slug is found.
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        
        # Call the parent's original `save` method to save the object to the database.
        super().save(*args, **kwargs)