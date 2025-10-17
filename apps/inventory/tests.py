# apps/inventory/tests.py
from django.test import TestCase
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from .models import Category
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