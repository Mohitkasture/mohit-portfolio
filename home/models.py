from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteProfile(TimeStampedModel):
    full_name = models.CharField(max_length=120, default="Mohit Kasture")
    headline = models.CharField(max_length=255, blank=True)
    subheadline = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    about = models.TextField(blank=True)
    focus_items = models.JSONField(default=list, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_username = models.CharField(max_length=80, blank=True, default="Mohit-flowcreafter")
    website_url = models.URLField(blank=True)
    current_role = models.CharField(max_length=255, blank=True)
    stack_line = models.CharField(max_length=255, blank=True)
    focus_line = models.CharField(max_length=255, blank=True)
    now_line = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Site profile"
        verbose_name_plural = "Site profile"

    def __str__(self):
        return self.full_name


class Experience(TimeStampedModel):
    title = models.CharField(max_length=120)
    company = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    period = models.CharField(max_length=80)
    summary = models.CharField(max_length=255, blank=True)
    bullets = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return f"{self.title} · {self.company}"


class Project(TimeStampedModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    kicker = models.CharField(max_length=255, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    contribution = models.TextField(blank=True)
    technical = models.TextField(blank=True)
    bullets = models.JSONField(default=list, blank=True)
    tech_stack = models.JSONField(default=list, blank=True)
    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    badge = models.CharField(max_length=80, blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title


class SkillCategory(TimeStampedModel):
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Skill categories"

    def __str__(self):
        return self.name


class Skill(TimeStampedModel):
    category = models.ForeignKey(
        SkillCategory,
        related_name="skills",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Education(TimeStampedModel):
    degree = models.CharField(max_length=160)
    institution = models.CharField(max_length=160)
    location = models.CharField(max_length=120, blank=True)
    period = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name_plural = "Education"

    def __str__(self):
        return self.degree


class KnowledgeChunk(TimeStampedModel):
    SOURCE_CHOICES = [
        ("profile", "Profile"),
        ("experience", "Experience"),
        ("project", "Project"),
        ("skill", "Skill"),
        ("education", "Education"),
        ("resume", "Resume"),
        ("github", "GitHub"),
        ("custom", "Custom"),
    ]
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=160)
    content = models.TextField()
    keywords = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["source_type", "title"]

    def __str__(self):
        return f"{self.source_type}: {self.title}"


class AnalyticsEvent(models.Model):
    EVENT_CHOICES = [
        ("page_view", "Page view"),
        ("project_view", "Project view"),
        ("resume_download", "Resume download"),
        ("github_click", "GitHub click"),
        ("contact_submit", "Contact submit"),
        ("ai_query", "AI query"),
        ("resume_analyze", "Resume analyze"),
        ("external_link", "External link"),
        ("npc_chat", "NPC chat"),
    ]
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES)
    path = models.CharField(max_length=255, blank=True)
    label = models.CharField(max_length=160, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    session_key = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} @ {self.created_at:%Y-%m-%d %H:%M}"


class GitHubRepoCache(TimeStampedModel):
    github_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=160)
    full_name = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    html_url = models.URLField()
    language = models.CharField(max_length=80, blank=True)
    stars = models.PositiveIntegerField(default=0)
    forks = models.PositiveIntegerField(default=0)
    topics = models.JSONField(default=list, blank=True)
    pushed_at = models.DateTimeField(null=True, blank=True)
    is_fork = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-stars", "-pushed_at"]
        verbose_name = "GitHub repo"
        verbose_name_plural = "GitHub repos"

    def __str__(self):
        return self.full_name


class EvaluationCase(TimeStampedModel):
    question = models.TextField()
    expected_keywords = models.JSONField(default=list, blank=True)
    expected_answer = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question[:80]


class EvaluationRun(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    passed = models.PositiveIntegerField(default=0)
    accuracy = models.FloatField(default=0)
    groundedness = models.FloatField(default=0)
    hallucination_rate = models.FloatField(default=0)
    details = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Eval {self.started_at:%Y-%m-%d %H:%M} · {self.accuracy:.0%}"


class GameNpc(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    display_name = models.CharField(max_length=120)
    persona = models.TextField()
    greeting = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name
