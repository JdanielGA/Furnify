# apps/inventory/tests.py
from django.test import TestCase
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from .models import Category, Product
from .forms import CategoryForm

# --- Tests for Models (Business Logic) ---
class CategoryModelTests(TestCase):
    """
    Test suite for the Category model.
    """

    def test_delete_parent_category_with_children_is_protected(self):
        """
        Verifies that a parent category cannot be deleted if it has children.
        This is an INTEGRATION test because it interacts with the database
        and validates an ORM rule (on_delete=PROTECT).
        """
        # 1. ARRANGE: Set up the scenario.
        # Create a parent category.
        parent_category = Category.objects.create(name="Office Furniture", slug="office")
        
        # Create a child category linked to the parent.
        Category.objects.create(name="Desk Chairs", slug="chairs", parent=parent_category)

        # 2. ACT & ASSERT: Perform the action and verify the result.
        # We use a context manager to verify that the correct exception is raised.
        # The code within the 'with' block is expected to fail.
        with self.assertRaises(ProtectedError):
            parent_category.delete()

        # 3. ASSERT (Post-condition): Verify the final state of the system.
        # Ensure the parent object still exists in the database.
        self.assertTrue(
            Category.objects.filter(pk=parent_category.pk).exists(),
            "The parent object should not have been deleted."
        )


# --- Tests for Views ---
class CategoryViewTests(TestCase):
    """
    Test suite for the Category views.
    """

    def setUp(self):
        """
        Sets up a test category before each test method runs.
        """
        self.category = Category.objects.create(name="Home", slug="home")

    def test_category_create_view_get_request(self):
        """
        Tests that the create view responds with HTTP 200 for GET requests.
        """
        # ACT: Make a GET request to the category creation URL.
        response = self.client.get(reverse('inventory:category_add'))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200, "The view should return a 200 status.")
        self.assertTemplateUsed(response, 'inventory/category_form.html', "The correct template should be used.")
        # Verify that the form is in the context.
        self.assertIn('form', response.context, "The context should contain a form.")
        self.assertIsInstance(response.context['form'], CategoryForm, "The form should be an instance of CategoryForm.")

    def test_category_create_view_post_success(self):
        """
        Tests that a valid POST request to the create view successfully creates a category.
        """
        # ARRANGE: Prepare the data for the new category.
        form_data = {
            'name': 'Chairs',
            'description': 'All chairs and seating options.',
            'parent': '',  # No parent category.
        }

        # ACT: Make a POST request to the category creation URL with the form data.
        response = self.client.post(reverse('inventory:category_add'), data=form_data)

        # ASSERT: Verify the conditions.
        # Check that the response is a redirect (HTTP 302).
        self.assertEqual(response.status_code, 302, "The view should redirect after successful creation.")
        # Verify that it redirects to the category list page.
        self.assertRedirects(response, reverse('inventory:category_list'))
        # Verify that the category was created in the database.
        self.assertTrue(
            Category.objects.filter(name='Chairs').exists(),
            "The new category should exist in the database."
        )

    def test_category_create_view_post_invalid_data(self):
        """
        Tests that an invalid POST request to the create view does not create a category.
        """
        # ARRANGE: Prepare invalid data (missing 'name' field).
        form_data = {
            'name': '',  # Name is required.
            'description': 'All tables and surfaces.',
            'parent': '',
        }

        # ACT: Make a POST request to the category creation URL with invalid data.
        response = self.client.post(reverse('inventory:category_add'), data=form_data)

        # ASSERT: Verify the conditions.
        # Check that the response status code is 200 (form re-rendered with errors).
        self.assertEqual(response.status_code, 200, "The view should return 200 for invalid form data.")
        self.assertTemplateUsed(response, 'inventory/category_form.html', "The correct template should be used.")
        # Verify that the form is in the context and contains errors.
        self.assertIn('form', response.context, "The context should contain a form.")
        form = response.context['form']
        self.assertIsInstance(form, CategoryForm, "The form should be an instance of CategoryForm.")
        self.assertTrue(form.errors, "The form should contain errors for invalid data.")
        # Verify that no new category was created in the database.
        self.assertFalse(
            Category.objects.filter(description='All tables and surfaces.').exists(),
            "No new category should have been created in the database."
        )

    def test_category_list_view_success_with_data(self):
        """
        Tests that the list view responds with HTTP 200 and uses the correct template
        when categories exist.
        """
        # ACT: Make a GET request to the category list URL.
        # We use reverse() to avoid hardcoding the URL.
        response = self.client.get(reverse('inventory:category_list'))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200, "The view should return a 200 status.")
        self.assertTemplateUsed(response, 'inventory/category_list.html', "The correct template should be used.")
    
    def test_category_list_view_empty_state(self):
        """
        Tests that the list view behaves correctly when there are no categories.
        """
        # ARRANGE: Delete the category created in setUp to simulate an empty database.
        self.category.delete()

        # ACT: Make the request to the view.
        response = self.client.get(reverse('inventory:category_list'))

        # ASSERT:
        self.assertEqual(response.status_code, 200)
        # NEW CONCEPT: assertContains.
        # Checks if the HTML content of the response contains specific text.
        # This allows us to verify that our {% empty %} block works.
        self.assertContains(response, "No categories available.")
        # We can also verify the opposite.
        self.assertQuerySetEqual(response.context['categories'], [], "The category queryset should be empty.")

    def test_category_detail_view_success(self):
        """
        Tests that the detail view for a category works correctly.
        """
        # ACT: Make a request to the detail URL using the slug of our test category.
        response = self.client.get(reverse('inventory:category_details', kwargs={'slug': self.category.slug}))

        # ASSERT:
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/category_details.html')
        # Verify that the context contains the category we expect.
        self.assertEqual(response.context['category'], self.category)

    def test_category_update_view_get_request(self):
        """
        Tests that the update view responds with HTTP 200 for GET requests.
        """
        # ACT: Make a GET request to the category update URL.
        response = self.client.get(reverse('inventory:category_edit', kwargs={'pk': self.category.pk}))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200, "The view should return a 200 status.")
        self.assertTemplateUsed(response, 'inventory/category_form.html', "The correct template should be used.")
        # Verify that the form is in the context.
        self.assertIn('form', response.context, "The context should contain a form.")
        self.assertIsInstance(response.context['form'], CategoryForm, "The form should be an instance of CategoryForm.")

    def test_category_update_view_post_success(self):
        """
        Tests that a valid POST request to the update view successfully updates a category.
        """
        # ARRANGE: Prepare the updated data for the category.
        form_data = {
            'name': 'Updated Home',
            'description': 'Updated description for home category.',
            'parent': '',  # No parent category.
        }

        # ACT: Make a POST request to the category update URL with the form data.
        response = self.client.post(reverse('inventory:category_edit', kwargs={'pk': self.category.pk}), data=form_data)

        # ASSERT: Verify the conditions.
        # Check that the response is a redirect (HTTP 302).
        self.assertEqual(response.status_code, 302, "The view should redirect after successful update.")
        # Verify that it redirects to the category list page.
        self.assertRedirects(response, reverse('inventory:category_list'))
        # Refresh the category from the database.
        self.category.refresh_from_db()
        # Verify that the category was updated in the database.
        self.assertEqual(self.category.name, 'Updated Home', "The category name should have been updated.")
        self.assertEqual(self.category.description, 'Updated description for home category.', "The category description should have been updated.")

    def test_category_update_view_post_invalid_data(self):
        """
        Tests that an invalid POST request to the update view does not update the category.
        """
        # ARRANGE: Prepare invalid data (empty 'name' field).
        form_data = {
            'name': '',  # Name is required.
            'description': 'This description should not be saved.',
            'parent': '',
        }

        # ACT: Make a POST request to the category update URL with invalid data.
        response = self.client.post(reverse('inventory:category_edit', kwargs={'pk': self.category.pk}), data=form_data)

        # ASSERT: Verify the conditions.
        # Check that the response status code is 200 (form re-rendered with errors).
        self.assertEqual(response.status_code, 200, "The view should return 200 for invalid form data.")
        self.assertTemplateUsed(response, 'inventory/category_form.html', "The correct template should be used.")
        # Verify that the form is in the context and contains errors.
        self.assertIn('form', response.context, "The context should contain a form.")
        form = response.context['form']
        self.assertIsInstance(form, CategoryForm, "The form should be an instance of CategoryForm.")
        self.assertTrue(form.errors, "The form should contain errors for invalid data.")
        # Refresh the category from the database.
        self.category.refresh_from_db()
        # Verify that the category was not updated in the database.
        self.assertNotEqual(self.category.description, 'This description should not be saved.', "The category description should not have been updated.")
        self.assertEqual(self.category.name, 'Home', "The category name should remain unchanged.")

    def test_category_delete_view_get_request(self):
        """
        Tests that the delete view responds with HTTP 200 for GET requests.
        """
        # ACT: Make a GET request to the category delete URL.
        response = self.client.get(reverse('inventory:category_delete', kwargs={'pk': self.category.pk}))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200, "The view should return a 200 status.")
        self.assertTemplateUsed(response, 'inventory/category_confirm_delete.html', "The correct template should be used.")
        # Verify that the category is in the context.
        self.assertIn('category', response.context, "The context should contain the category.")
        self.assertEqual(response.context['category'], self.category, "The context category should be the one to be deleted.")

    def test_category_delete_view_post_request(self):
        """
        Tests that a POST request to the delete view deletes the category.
        """
        # ARRANGE: Verify the category exists before deletion.
        category_pk = self.category.pk
        self.assertTrue(Category.objects.filter(pk=category_pk).exists())

        # ACT: Make a POST request to the category delete URL.
        response = self.client.post(reverse('inventory:category_delete', kwargs={'pk': category_pk}))

        # ASSERT: Verify the redirection after deletion.
        self.assertEqual(response.status_code, 302, "The view should redirect after deletion.")
        self.assertRedirects(response, reverse('inventory:category_list'))
        # Verify that the category was deleted from the database.
        self.assertFalse(Category.objects.filter(pk=category_pk).exists(), "The category should have been deleted from the database.")

# --- Tests for Product Model ---
class ProductModelTests(TestCase):
    """
    Test suite for the Product model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Sets up a test category to be used for product tests.
        This runs once for the entire TestCase.
        """
        cls.category = Category.objects.create(name="Chairs", slug="chairs")

    
    def test_product_slug_is_autogenerated(self):
        """
        Verifies that the slug for a Product is automatically generated from its name if not provided.
        """
        # ARRANGE: Create a product without specifying a slug.
        product = Product.objects.create(
            name="Ergonomic Chair",
            category=self.category,
            price=199.99,
            stock=10
        )

        # ASSERT: Verify that the slug was autogenerated correctly.
        self.assertEqual(product.slug, "ergonomic-chair", "The slug should be autogenerated from the product name.")

    def test_product_slug_is_unique_with_suffix(self):
        """
        Verifies that the slug for a Product is made unique by appending a suffix if a duplicate exists.
        """
        # ARRANGE: Create the first product with a specific name.
        Product.objects.create(
            name="Office Chair",
            category=self.category,
            price=149.99,
            stock=5
        )

        # ACT: Create a second product with the same name.
        second_product = Product.objects.create(
            name="Office Chair",
            category=self.category,
            price=159.99,
            stock=8
        )

        # ASSERT: Verify that the second product's slug has a suffix to ensure uniqueness.
        self.assertEqual(second_product.slug, "office-chair-1", "The slug should have a '-1' suffix to ensure uniqueness.")

    def test_deleting_category_with_products_is_protected(self):
        """
        Verifies that a category cannot be deleted if it has associated products.
        This tests the on_delete=PROTECT behavior of the ForeignKey relationship.
        """
        # ARRANGE: Create a product linked to the test category.
        Product.objects.create(
            name="Gaming Chair",
            category=self.category,
            price=299.99,
            stock=7
        )

        # ACT & ASSERT: Attempt to delete the category and expect a ProtectedError.
        with self.assertRaises(ProtectedError):
            self.category.delete()

        # ASSERT (Post-condition): Verify the category still exists.
        self.assertTrue(
            Category.objects.filter(pk=self.category.pk).exists(),
            "The category should not have been deleted since it has associated products."
        )


class ProductViewTests(TestCase):
    """
    Test suite for the Product views.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data once for the entire test class.
        We create two categories and two products to have realistic test data.
        """
        cls.category1 = Category.objects.create(name="Tables", slug="tables")
        cls.category2 = Category.objects.create(name="Sofas", slug="sofas")

        cls.product1 = Product.objects.create(
            name="Dining Table",
            category=cls.category1,
            price=499.99,
            stock=3
        )

        cls.product2 = Product.objects.create(
            name="Leather Sofa",
            category=cls.category2,
            price=899.99,
            stock=2
        )

    def test_product_list_view_success_with_data(self):
        """
        Tests that the product list view responds with HTTP 200 and uses the correct template
        when products exist.
        """
        # ACT: Make a GET request to the product list URL.
        response = self.client.get(reverse('inventory:product_list'))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200, "The view should return a 200 status.")
        self.assertTemplateUsed(response, 'inventory/product_list.html', "The correct template should be used.")
        # Verify that the context contains the products we created.
        self.assertIn('products', response.context, "The context should contain products.")
        products = response.context['products']
        self.assertEqual(len(products), 2, "There should be two products in the context.")
        self.assertIn(self.product1, products, "Product1 should be in the context.")
        self.assertIn(self.product2, products, "Product2 should be in the context.")

    def test_product_list_view_empty_state(self):
        """
        Tests that the product list view behaves correctly when there are no products.
        """
        # ARRANGE: Delete all products to simulate an empty database.
        Product.objects.all().delete()

        # ACT: Make the request to the view.
        response = self.client.get(reverse('inventory:product_list'))

        # ASSERT:
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products available.")
        self.assertQuerySetEqual(response.context['products'], [], "The product queryset should be empty.")

    def test_product_list_view_optimization_with_select_related(self):
        """
        Tests that the product list view uses select_related to optimize database queries.
        This helps prevent the N+1 query problem when accessing related category data.
        """
        # ACT: Make a GET request to the product list URL.
        with self.assertNumQueries(1):
            response = self.client.get(reverse('inventory:product_list'))

        # ASSERT: Verify the conditions.
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        for product in products:
            # Accessing the related category should not trigger additional queries.
            _ = product.category.name