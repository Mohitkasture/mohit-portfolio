from rest_framework import serializers

from home import models


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = (
            "id",
            "title",
            "slug",
            "kicker",
            "tagline",
            "overview",
            "contribution",
            "technical",
            "bullets",
            "tech_stack",
            "live_url",
            "github_url",
            "badge",
            "featured",
            "order",
            "view_count",
        )
        read_only_fields = ("view_count",)


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Experience
        fields = (
            "id",
            "title",
            "company",
            "location",
            "period",
            "summary",
            "bullets",
            "order",
        )


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = ("id", "name", "order")


class SkillCategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = models.SkillCategory
        fields = ("id", "name", "order", "skills")


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Education
        fields = ("id", "degree", "institution", "location", "period", "order")


class SiteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteProfile
        fields = (
            "full_name",
            "headline",
            "subheadline",
            "location",
            "about",
            "focus_items",
            "email",
            "phone",
            "linkedin_url",
            "github_username",
            "website_url",
            "current_role",
            "stack_line",
            "focus_line",
            "now_line",
        )


class GitHubRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GitHubRepoCache
        fields = (
            "id",
            "name",
            "full_name",
            "description",
            "html_url",
            "language",
            "stars",
            "forks",
            "topics",
            "pushed_at",
            "is_fork",
        )


class EvaluationRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EvaluationRun
        fields = (
            "id",
            "started_at",
            "finished_at",
            "total",
            "passed",
            "accuracy",
            "groundedness",
            "hallucination_rate",
            "details",
        )
