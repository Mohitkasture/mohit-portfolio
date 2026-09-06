from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_ok(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mohit Kasture")
        self.assertNotContains(response, "<span>Gmail</span>")
        self.assertContains(response, "Django REST Framework")
        self.assertContains(response, "<h3>Testing</h3>")

    def test_contact_requires_fields(self):
        response = self.client.post(reverse("home:index"), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please fill in all fields.")


class ResumePdfTests(TestCase):
    def test_skills_exclude_gmail_as_a_skill(self):
        pdf = Path(settings.BASE_DIR) / "home/static/home/files/Mohit-Kasture-resume.pdf"
        data = pdf.read_bytes()
        self.assertNotIn(b"Python Django Gmail", data)
        self.assertIn(b"Django REST Framework", data)
        self.assertIn(b"Backend:", data)
        self.assertIn(b"Testing:", data)
