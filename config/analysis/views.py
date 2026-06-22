from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DueDiligenceSession
from .serializers import (
    AskQuestionSerializer,
    AnalysisReportSerializer,
    DueDiligenceSessionSerializer,
    QuestionSerializer,
)
from .services.rag_pipeline import ask_question, generate_report


class DueDiligenceSessionViewSet(viewsets.ModelViewSet):
    """
    POST   /api/analysis/sessions/                  -> create a session for a company
    GET    /api/analysis/sessions/                   -> list your sessions
    GET    /api/analysis/sessions/{id}/              -> retrieve one (with reports + Q&A)
    POST   /api/analysis/sessions/{id}/generate_report/  -> run full RAG report generation
    POST   /api/analysis/sessions/{id}/ask/          -> ask an ad-hoc grounded question
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DueDiligenceSessionSerializer

    def get_queryset(self):
        return DueDiligenceSession.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def generate_report(self, request, pk=None):
        session = self.get_object()
        try:
            report = generate_report(session)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AnalysisReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def ask(self, request, pk=None):
        session = self.get_object()
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            question = ask_question(session, serializer.validated_data["question"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
