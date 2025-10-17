# apps/inventory/tests.py
from django.test import TestCase
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from .models import Category

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