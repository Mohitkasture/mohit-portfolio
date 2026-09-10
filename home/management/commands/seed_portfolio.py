from django.core.management.base import BaseCommand

from home.models import (
    Education,
    EvaluationCase,
    Experience,
    GameNpc,
    KnowledgeChunk,
    Project,
    SiteProfile,
    Skill,
    SkillCategory,
)


def rebuild_knowledge():
    KnowledgeChunk.objects.filter(source_type__in=[
        "profile", "experience", "project", "skill", "education", "custom",
    ]).delete()

    profile = SiteProfile.objects.first()
    if profile:
        KnowledgeChunk.objects.create(
            source_type="profile",
            source_id=str(profile.pk),
            title="About Mohit",
            content=(
                f"{profile.full_name}. {profile.headline}. {profile.subheadline}. "
                f"Location: {profile.location}. {profile.about} "
                f"Current role: {profile.current_role}. "
                f"Focus: {', '.join(profile.focus_items or [])}."
            ),
            keywords=["mohit", "backend", "django", "python", "ahmedabad", "ai"],
        )

    for exp in Experience.objects.filter(is_visible=True):
        KnowledgeChunk.objects.create(
            source_type="experience",
            source_id=str(exp.pk),
            title=f"{exp.title} at {exp.company}",
            content=(
                f"{exp.title} at {exp.company} ({exp.period}). {exp.summary}. "
                + " ".join(exp.bullets or [])
            ),
            keywords=[exp.company.lower(), "experience", "backend", "django"],
        )

    for project in Project.objects.filter(is_visible=True):
        KnowledgeChunk.objects.create(
            source_type="project",
            source_id=str(project.pk),
            title=project.title,
            content=(
                f"{project.title}: {project.tagline}. Overview: {project.overview}. "
                f"Contribution: {project.contribution}. Technical: {project.technical}. "
                f"Stack: {', '.join(project.tech_stack or [])}. "
                + " ".join(project.bullets or [])
            ),
            keywords=[project.title.lower(), *(project.tech_stack or []), "project"],
        )

    for cat in SkillCategory.objects.filter(is_visible=True).prefetch_related("skills"):
        names = [s.name for s in cat.skills.filter(is_visible=True)]
        KnowledgeChunk.objects.create(
            source_type="skill",
            source_id=str(cat.pk),
            title=f"Skills — {cat.name}",
            content=f"{cat.name} skills: {', '.join(names)}.",
            keywords=[cat.name.lower(), *[n.lower() for n in names], "skills"],
        )

    for edu in Education.objects.filter(is_visible=True):
        KnowledgeChunk.objects.create(
            source_type="education",
            source_id=str(edu.pk),
            title=edu.degree,
            content=f"{edu.degree} at {edu.institution} ({edu.period}).",
            keywords=["education", "mca", "bsc"],
        )

    KnowledgeChunk.objects.create(
        source_type="custom",
        source_id="ai",
        title="AI engineering on this portfolio",
        content=(
            "This portfolio implements a RAG assistant over portfolio knowledge, "
            "semantic project search with embeddings-style retrieval, resume analysis "
            "combining regex extraction and LLM suggestions, an AI evaluation pipeline "
            "for accuracy/groundedness/hallucinations, analytics insights, and an AI game NPC."
        ),
        keywords=["rag", "ai", "llm", "evaluation", "embeddings", "assistant"],
    )


class Command(BaseCommand):
    help = "Seed portfolio CMS content, evaluation cases, and knowledge chunks"

    def handle(self, *args, **options):
        profile, _ = SiteProfile.objects.get_or_create(
            pk=1,
            defaults={
                "full_name": "Mohit Kasture",
                "headline": "Python & Django Developer building production-ready APIs and backend systems",
                "subheadline": (
                    "I build REST APIs, database-backed applications, and backend features "
                    "that connect reliably with frontend and third-party services."
                ),
                "location": "Ahmedabad, Gujarat, India",
                "about": (
                    "Python and Django developer focused on backend systems, REST API design, "
                    "and PostgreSQL. I write clean Django code and work with frontend teams to "
                    "ship features that hold up in production."
                ),
                "focus_items": [
                    "Django REST Framework and REST APIs",
                    "PostgreSQL schemas and data workflows",
                    "Frontend–backend integration",
                    "Git, GitHub, and environment configuration",
                    "AI-integrated backend features (RAG, LLM APIs)",
                ],
                "email": "mkymohitkumaryadav0@gmail.com",
                "phone": "+91 88172 84530",
                "linkedin_url": "https://www.linkedin.com/in/mohit-kasture-812a44261",
                "github_username": "Mohit-flowcreafter",
                "website_url": "https://mohit-portfolio-0vmy.onrender.com",
                "current_role": "Python Developer at AppUnik, Ahmedabad — Jan 2026 to present.",
                "stack_line": "Python · Django · PostgreSQL",
                "focus_line": "REST APIs · backend systems · AI integrations",
                "now_line": "AppUnik · Ahmedabad",
            },
        )

        if not Experience.objects.exists():
            Experience.objects.bulk_create(
                [
                    Experience(
                        title="Python Developer",
                        company="AppUnik",
                        location="Ahmedabad",
                        period="Jan 2026 – Present",
                        summary="Enterprise web solutions",
                        bullets=[
                            "Designed and implemented REST APIs with Python and Django for core business workflows and frontend integrations.",
                            "Designed PostgreSQL schemas and data relationships for storage, processing, and application workflows.",
                            "Implemented backend features for user data management and API integrations.",
                            "Kept frontend–backend communication reliable through structured, documented API contracts.",
                        ],
                        order=0,
                    ),
                    Experience(
                        title="Backend Intern",
                        company="AppUnik",
                        location="Ahmedabad",
                        period="Sep 2025 – Dec 2025",
                        summary="",
                        bullets=[
                            "Wrote PostgreSQL queries and worked on schema changes for application data.",
                            "Used Git and GitHub for feature branches, commits, and pull requests.",
                            "Followed main vs development branch workflows on live project code.",
                            "Configured environments with .env files so credentials stay out of source.",
                        ],
                        order=1,
                    ),
                    Experience(
                        title="Software Intern",
                        company="Qspider",
                        location="Ahmedabad",
                        period="Mar 2025 – Sep 2025",
                        summary="Python, SQL, Django, manual testing",
                        bullets=[
                            "Practiced Python problem-solving for backend-oriented tasks.",
                            "Wrote SQL for retrieval and updates across relational tables.",
                            "Learned manual testing: test cases, testing types, and SDLC / STLC.",
                        ],
                        order=2,
                    ),
                ]
            )

        if not Project.objects.exists():
            Project.objects.bulk_create(
                [
                    Project(
                        title="Flowcreator",
                        slug="flowcreator",
                        kicker="Featured · AI content SaaS · Nov 2025 – Feb 2026",
                        tagline="AI-powered social content SaaS",
                        overview=(
                            "An AI-powered platform for generating captions and images for social media, "
                            "with scheduling, publishing, role-based access, and subscription billing in one product."
                        ),
                        contribution=(
                            "Built Django backend APIs and workflows for content generation, scheduling, "
                            "publishing, role-based access control, and billing."
                        ),
                        technical="",
                        bullets=[
                            "Django backend and REST API development for the product’s core workflows",
                            "AI content generation workflows: caption generation with prompt enhancement and tone selection, and image generation from user inputs",
                            "Scheduling and publishing workflows for automated posting",
                            "Role-based access control",
                            "Subscription billing",
                        ],
                        tech_stack=[
                            "Python",
                            "Django",
                            "PostgreSQL",
                            "REST APIs",
                            "AI integrations",
                            "Authentication / RBAC",
                            "Subscription / billing",
                        ],
                        live_url="https://flowcreator.dev",
                        featured=True,
                        order=0,
                    ),
                    Project(
                        title="Meditation App",
                        slug="meditation-app",
                        kicker="Meditation app · Mar 2026 · Ahmedabad",
                        tagline="",
                        overview=(
                            "A meditation app backend for user management and session tracking, "
                            "with a documented API contract the frontend can depend on."
                        ),
                        contribution=(
                            "Built Django REST APIs and PostgreSQL-backed storage for users, sessions, "
                            "completion tracking, and activity updates."
                        ),
                        technical=(
                            "Django REST APIs over PostgreSQL for profiles, session records, and "
                            "user-related writes — structured so the frontend can rely on a stable contract."
                        ),
                        bullets=[
                            "REST APIs in Django for user management and meditation session tracking",
                            "PostgreSQL for user profiles and session records",
                            "Session completion tracking and user activity updates",
                            "Documented APIs so frontend and backend stay in sync",
                        ],
                        tech_stack=[
                            "Python",
                            "Django",
                            "Django REST Framework",
                            "REST APIs",
                            "PostgreSQL",
                        ],
                        badge="Private · case study",
                        featured=False,
                        order=1,
                    ),
                    Project(
                        title="AI Portfolio Platform",
                        slug="ai-portfolio-platform",
                        kicker="Flagship · Backend + AI · 2026",
                        tagline="Production-style portfolio with RAG, CMS APIs, and evaluation",
                        overview=(
                            "This portfolio itself: Django CMS content, DRF APIs, JWT-protected admin "
                            "mutations, RAG assistant, GitHub sync, analytics, resume analyzer, and AI eval."
                        ),
                        contribution=(
                            "Designed and implemented the full backend architecture, knowledge retrieval, "
                            "and measurable AI evaluation pipeline."
                        ),
                        technical=(
                            "Django + DRF + SimpleJWT, TF-IDF style retrieval over KnowledgeChunk, "
                            "Groq LLM generation, regex+LLM resume analysis, Dockerized deploy path."
                        ),
                        bullets=[
                            "RAG portfolio assistant grounded in CMS knowledge",
                            "Semantic project search",
                            "Admin CMS + REST APIs",
                            "GitHub live repo integration",
                            "Analytics + AI insights",
                            "Resume analyzer (regex + LLM)",
                            "AI evaluation for accuracy / groundedness / hallucinations",
                        ],
                        tech_stack=[
                            "Python",
                            "Django",
                            "Django REST Framework",
                            "JWT",
                            "PostgreSQL",
                            "RAG",
                            "LLM",
                            "Docker",
                            "GitHub Actions",
                        ],
                        featured=True,
                        order=2,
                    ),
                ]
            )

        if not SkillCategory.objects.exists():
            mapping = {
                "Backend": ["Python", "Django", "Django REST Framework", "REST APIs", "JWT"],
                "Database": ["PostgreSQL", "SQL", "RDBMS"],
                "AI": ["LLM APIs", "RAG", "Embeddings retrieval", "Prompt engineering"],
                "Frontend": ["HTML", "CSS", "JavaScript", "React"],
                "Tools": ["Git", "GitHub", "Docker", "GitHub Actions"],
                "Testing": ["Manual Testing", "SDLC", "STLC", "Django TestCase"],
            }
            for i, (name, skills) in enumerate(mapping.items()):
                cat = SkillCategory.objects.create(name=name, order=i)
                Skill.objects.bulk_create(
                    [Skill(category=cat, name=s, order=j) for j, s in enumerate(skills)]
                )

        if not Education.objects.exists():
            Education.objects.bulk_create(
                [
                    Education(
                        degree="Master of Computer Applications (MCA)",
                        institution="Rajiv Gandhi Proudyogiki Vishwavidyalaya",
                        location="Bhopal",
                        period="Jul 2023 – May 2025",
                        order=0,
                    ),
                    Education(
                        degree="Bachelor of Science (BSc)",
                        institution="Barkatullah University",
                        location="Bhopal",
                        period="Jul 2020 – May 2023",
                        order=1,
                    ),
                ]
            )

        if not EvaluationCase.objects.exists():
            EvaluationCase.objects.bulk_create(
                [
                    EvaluationCase(
                        question="What backend technologies does Mohit use?",
                        expected_keywords=["Python", "Django", "PostgreSQL"],
                        category="skills",
                    ),
                    EvaluationCase(
                        question="What projects has Mohit built?",
                        expected_keywords=["Flowcreator", "Meditation"],
                        category="projects",
                    ),
                    EvaluationCase(
                        question="Where does Mohit work currently?",
                        expected_keywords=["AppUnik"],
                        category="experience",
                    ),
                    EvaluationCase(
                        question="Which projects demonstrate backend and AI?",
                        expected_keywords=["Flowcreator", "AI"],
                        category="projects",
                    ),
                    EvaluationCase(
                        question="What is Mohit's education background?",
                        expected_keywords=["MCA", "Bhopal"],
                        category="education",
                    ),
                    EvaluationCase(
                        question="Does Mohit know Django REST Framework?",
                        expected_keywords=["Django REST Framework", "DRF", "REST"],
                        category="skills",
                    ),
                    EvaluationCase(
                        question="Tell me about Flowcreator",
                        expected_keywords=["Flowcreator", "AI", "Django"],
                        category="projects",
                    ),
                    EvaluationCase(
                        question="What city is Mohit based in?",
                        expected_keywords=["Ahmedabad"],
                        category="profile",
                    ),
                ]
            )

        GameNpc.objects.get_or_create(
            name="guide",
            defaults={
                "display_name": "Asha the Guide",
                "persona": (
                    "You are Asha, a witty game NPC living inside Mohit Kasture's portfolio. "
                    "You know Mohit is a Python/Django backend developer who builds AI-backed systems "
                    "and game experiments. Keep replies playful and under 3 sentences. "
                    "Never invent fake employers."
                ),
                "greeting": "Welcome, traveler. Ask about Mohit's backend quests, AI gear, or game builds.",
            },
        )

        rebuild_knowledge()
        self.stdout.write(self.style.SUCCESS(
            f"Seeded profile={profile.full_name}, "
            f"projects={Project.objects.count()}, "
            f"chunks={KnowledgeChunk.objects.count()}"
        ))
