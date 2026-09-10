from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from home.models import KnowledgeChunk, Project
from home.services.resume_analyzer import analyze_resume, rule_based_extract
from home.services.rag import answer_question, semantic_project_search


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_portfolio")


class HomePageTests(SeededTestCase):
    def test_home_ok(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mohit Kasture")
        self.assertNotContains(response, "<span>Gmail</span>")
        self.assertContains(response, "Django REST Framework")
        self.assertContains(response, "<h3>Testing</h3>")
        self.assertContains(response, "Ask Mohit AI")

    def test_contact_requires_fields(self):
        response = self.client.post(reverse("home:index"), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please fill in all fields.")


class ResumePdfTests(TestCase):
    def test_skills_exclude_gmail_as_a_skill(self):
        pdf = Path(settings.BASE_DIR) / "home/static/home/files/Mohit-Kasture-resume.pdf"
        data = pdf.read_bytes()
        self.assertNotIn(b"Python Django Gmail", data)
        self.assertGreater(pdf.stat().st_size, 50_000)


class ApiTests(SeededTestCase):
    def test_projects_api(self):
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_assistant_api(self):
        response = self.client.post(
            "/api/assistant/",
            data={"question": "What backend technologies does Mohit use?"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("answer", payload)
        self.assertTrue(KnowledgeChunk.objects.exists())

    def test_project_search(self):
        hits = semantic_project_search("Django and AI")
        self.assertTrue(hits)
        response = self.client.get("/api/projects/search/?q=Django%20AI")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["results"])

    def test_analytics_track(self):
        response = self.client.post(
            "/api/analytics/track/",
            data={"event_type": "resume_download", "label": "cv"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_resume_analyzer_rules(self):
        text = (
            "Mohit Kasture\nemail: mohit@example.com\nphone: +91 88172 84530\n"
            "github.com/Mohitkasture\nPython Django PostgreSQL REST APIs developer experience "
            "built projects with Docker"
        )
        extracted = rule_based_extract(text)
        self.assertTrue(extracted["emails"])
        self.assertIn("python", extracted["matched_keywords"])
        result = analyze_resume(text)
        self.assertGreaterEqual(result["scores"]["ats_score"], 50)

    def test_resume_analyze_api(self):
        response = self.client.post(
            "/api/resume/analyze/",
            data={
                "text": (
                    "Jane Doe jane@mail.com +1 555 123 4567 github.com/jane "
                    "Python Django experience built REST API projects PostgreSQL"
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("scores", response.json())

    def test_npc_api(self):
        response = self.client.post(
            "/api/npc/",
            data={"message": "Tell me about backend work"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.json())

    def test_rag_answer_mentions_stack(self):
        result = answer_question("What backend technologies does Mohit use?")
        lower = result["answer"].lower()
        self.assertNotIn("knowledge base", lower)
        self.assertTrue(
            "django" in lower or "python" in lower or "postgresql" in lower,
            result["answer"],
        )

    def test_assistant_projects_question(self):
        result = answer_question("What projects has Mohit built?")
        lower = result["answer"].lower()
        self.assertNotIn("knowledge base", lower)
        self.assertTrue("flowcreator" in lower or "meditation" in lower, result["answer"])

    def test_assistant_smalltalk_name(self):
        result = answer_question("hi what is your name")
        self.assertEqual(result["mode"], "smalltalk")
        lower = result["answer"].lower()
        self.assertIn("ask mohit ai", lower)
        self.assertNotIn("virtual assistant", lower)
        self.assertNotIn("knowledge base", lower)

    def test_assistant_role_sources(self):
        result = answer_question("tell me mohit current roll of his company")
        lower = result["answer"].lower()
        self.assertTrue("python" in lower or "appunik" in lower, result["answer"])
        source_types = {s["source_type"] for s in result["sources"]}
        self.assertTrue(source_types <= {"experience", "profile"}, result["sources"])
        titles = " ".join(s["title"].lower() for s in result["sources"])
        self.assertNotIn("bachelor", titles)
        self.assertNotIn("master", titles)


class ProjectModelTests(SeededTestCase):
    def test_flowcreator_seeded(self):
        self.assertTrue(Project.objects.filter(slug="flowcreator").exists())
