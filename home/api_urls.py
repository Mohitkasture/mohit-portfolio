from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from home import api_views

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", api_views.ProfileAPI.as_view(), name="api-profile"),
    path("projects/", api_views.ProjectListCreateAPI.as_view(), name="api-projects"),
    path("projects/search/", api_views.ProjectSearchAPI.as_view(), name="api-project-search"),
    path("projects/<slug:slug>/", api_views.ProjectDetailAPI.as_view(), name="api-project-detail"),
    path("experience/", api_views.ExperienceListAPI.as_view(), name="api-experience"),
    path("skills/", api_views.SkillCategoryListAPI.as_view(), name="api-skills"),
    path("education/", api_views.EducationListAPI.as_view(), name="api-education"),
    path("github/repos/", api_views.GitHubRepoListAPI.as_view(), name="api-github-repos"),
    path("github/sync/", api_views.GitHubSyncAPI.as_view(), name="api-github-sync"),
    path("assistant/", api_views.AssistantAPI.as_view(), name="api-assistant"),
    path("analytics/track/", api_views.AnalyticsTrackAPI.as_view(), name="api-analytics-track"),
    path("analytics/summary/", api_views.AnalyticsSummaryAPI.as_view(), name="api-analytics-summary"),
    path("analytics/insights/", api_views.AnalyticsInsightsAPI.as_view(), name="api-analytics-insights"),
    path("resume/analyze/", api_views.ResumeAnalyzeAPI.as_view(), name="api-resume-analyze"),
    path("evaluation/", api_views.EvaluationRunAPI.as_view(), name="api-evaluation"),
    path("npc/", api_views.NpcChatAPI.as_view(), name="api-npc"),
]
