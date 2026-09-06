from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_ok(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mohit Kasture")

    def test_contact_requires_fields(self):
        response = self.client.post(reverse("home:index"), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please fill in all fields.")
