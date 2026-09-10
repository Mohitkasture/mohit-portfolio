from django.db.models import F
from rest_framework import generics, permissions, views
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from home import models, serializers
from home.services import analytics as analytics_service
from home.services import evaluation as evaluation_service
from home.services import github as github_service
from home.services import npc as npc_service
from home.services import rag
from home.services import resume_analyzer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class ProfileAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        profile = models.SiteProfile.objects.first()
        if not profile:
            return Response({"detail": "Profile not seeded yet."}, status=404)
        return Response(serializers.SiteProfileSerializer(profile).data)


class ProjectListCreateAPI(generics.ListCreateAPIView):
    serializer_class = serializers.ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = models.Project.objects.filter(is_visible=True)
        q = self.request.query_params.get("q")
        if q:
            hits = rag.semantic_project_search(q)
            ids = [p.id for _, p in hits]
            return qs.filter(id__in=ids)
        return qs


class ProjectDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    queryset = models.Project.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        models.Project.objects.filter(pk=instance.pk).update(view_count=F("view_count") + 1)
        instance.refresh_from_db()
        analytics_service.track_event(
            "project_view",
            path=request.path,
            label=instance.title,
            session_key=request.session.session_key or "",
        )
        return Response(self.get_serializer(instance).data)


class ExperienceListAPI(generics.ListAPIView):
    serializer_class = serializers.ExperienceSerializer
    queryset = models.Experience.objects.filter(is_visible=True)


class SkillCategoryListAPI(generics.ListAPIView):
    serializer_class = serializers.SkillCategorySerializer
    queryset = models.SkillCategory.objects.filter(is_visible=True).prefetch_related("skills")


class EducationListAPI(generics.ListAPIView):
    serializer_class = serializers.EducationSerializer
    queryset = models.Education.objects.filter(is_visible=True)


class GitHubRepoListAPI(generics.ListAPIView):
    serializer_class = serializers.GitHubRepoSerializer
    queryset = models.GitHubRepoCache.objects.filter(is_visible=True, is_fork=False)


class GitHubSyncAPI(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        count = github_service.sync_github_repos()
        return Response({"synced": count})


class AssistantAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        question = (request.data.get("question") or "").strip()
        if not question:
            return Response({"detail": "question is required"}, status=400)
        if len(question) > 500:
            return Response({"detail": "question too long"}, status=400)
        result = rag.answer_question(question)
        analytics_service.track_event(
            "ai_query",
            path="/api/assistant/",
            label=question[:160],
            metadata={"mode": result.get("mode")},
            session_key=getattr(request.session, "session_key", "") or "",
        )
        return Response(result)


class ProjectSearchAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"results": []})
        hits = rag.semantic_project_search(q)
        data = [
            {
                "score": round(score, 3),
                "project": serializers.ProjectSerializer(project).data,
            }
            for score, project in hits[:10]
        ]
        return Response({"results": data})


class AnalyticsTrackAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        event_type = (request.data.get("event_type") or "").strip()
        allowed = {c[0] for c in models.AnalyticsEvent.EVENT_CHOICES}
        if event_type not in allowed:
            return Response({"detail": "invalid event_type"}, status=400)
        if not request.session.session_key:
            request.session.create()
        analytics_service.track_event(
            event_type,
            path=request.data.get("path") or "",
            label=(request.data.get("label") or "")[:160],
            metadata=request.data.get("metadata") or {},
            session_key=request.session.session_key,
        )
        return Response({"ok": True})


class AnalyticsSummaryAPI(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get("days") or 30)
        return Response(analytics_service.summary(days=days))


class AnalyticsInsightsAPI(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get("days") or 30)
        return Response(analytics_service.ai_insights(days=days))


class ResumeAnalyzeAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        upload = request.FILES.get("file")
        if upload and not text:
            raw = upload.read()
            text = resume_analyzer.extract_text_from_pdf(raw)
            if not text:
                try:
                    text = raw.decode("utf-8", errors="ignore")
                except Exception:
                    text = ""
        if not text or len(text) < 40:
            return Response(
                {"detail": "Provide resume text or a PDF/TXT file with extractable content."},
                status=400,
            )
        result = resume_analyzer.analyze_resume(text)
        analytics_service.track_event(
            "resume_analyze",
            path="/api/resume/analyze/",
            label="upload" if upload else "text",
            session_key=getattr(request.session, "session_key", "") or "",
        )
        return Response(result)


class EvaluationRunAPI(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        latest = models.EvaluationRun.objects.first()
        if not latest:
            return Response({"detail": "No evaluation runs yet."}, status=404)
        return Response(serializers.EvaluationRunSerializer(latest).data)

    def post(self, request):
        run = evaluation_service.run_evaluation()
        return Response(serializers.EvaluationRunSerializer(run).data)


class NpcChatAPI(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        npc_name = (request.data.get("npc") or "guide").strip()
        if not message:
            return Response({"detail": "message is required"}, status=400)
        result = npc_service.npc_reply(message, npc_name=npc_name)
        analytics_service.track_event(
            "npc_chat",
            path="/api/npc/",
            label=message[:160],
            session_key=getattr(request.session, "session_key", "") or "",
        )
        return Response(result)
