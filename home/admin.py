from django.contrib import admin

from home import models


@admin.register(models.SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "location", "current_role", "updated_at")


@admin.register(models.Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "period", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("title", "company")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "order", "view_count", "is_visible")
    list_editable = ("featured", "order", "is_visible")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "overview", "tech_stack")


class SkillInline(admin.TabularInline):
    model = models.Skill
    extra = 1


@admin.register(models.SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_visible")
    list_editable = ("order", "is_visible")
    inlines = [SkillInline]


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "order", "is_visible")
    list_filter = ("category",)


@admin.register(models.Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "period", "order", "is_visible")
    list_editable = ("order", "is_visible")


@admin.register(models.KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("title", "source_type", "is_active", "updated_at")
    list_filter = ("source_type", "is_active")
    search_fields = ("title", "content")


@admin.register(models.AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "label", "path", "created_at")
    list_filter = ("event_type",)
    readonly_fields = ("created_at",)


@admin.register(models.GitHubRepoCache)
class GitHubRepoCacheAdmin(admin.ModelAdmin):
    list_display = ("name", "language", "stars", "is_visible", "pushed_at")
    list_editable = ("is_visible",)
    search_fields = ("name", "description")


@admin.register(models.EvaluationCase)
class EvaluationCaseAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_active")
    list_filter = ("category", "is_active")


@admin.register(models.EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "accuracy", "groundedness", "hallucination_rate", "total")
    readonly_fields = ("started_at", "finished_at", "details")


@admin.register(models.GameNpc)
class GameNpcAdmin(admin.ModelAdmin):
    list_display = ("display_name", "name", "is_active")
