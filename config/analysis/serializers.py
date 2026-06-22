from rest_framework import serializers

from documents.serializers import DocumentChunkSerializer
from documents.models import Document

from .models import AnalysisReport, Citation, DueDiligenceSession, Question


class CitationSerializer(serializers.ModelSerializer):
    chunk = DocumentChunkSerializer(read_only=True)
    document_title = serializers.CharField(source="chunk.document.title", read_only=True)
    page_number = serializers.IntegerField(source="chunk.page_number", read_only=True)

    class Meta:
        model = Citation
        fields = ["id", "claim_excerpt", "document_title", "page_number", "chunk"]


class AnalysisReportSerializer(serializers.ModelSerializer):
    citations = CitationSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisReport
        fields = [
            "id",
            "executive_summary",
            "risk_assessment",
            "growth_opportunities",
            "citations",
            "generated_at",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    citations = CitationSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "answer_text", "citations", "asked_at"]


class DueDiligenceSessionSerializer(serializers.ModelSerializer):
    reports = AnalysisReportSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = DueDiligenceSession
        fields = ["id", "company_name", "documents", "reports", "questions", "created_at"]

    def validate_documents(self, documents):
        request = self.context["request"]
        for doc in documents:
            if doc.owner_id != request.user.id:
                raise serializers.ValidationError("You can only attach your own documents.")
        return documents


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
