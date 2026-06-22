from django.conf import settings
from django.db import models

from documents.models import Document


class DueDiligenceSession(models.Model):
    """
    One due-diligence engagement for a target company, grouping together
    every Document the analyst has uploaded for it. A session can have many
    AnalysisReports (re-run over time as new documents are added) and many
    ad-hoc Questions.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions"
    )
    company_name = models.CharField(max_length=255)
    documents = models.ManyToManyField(Document, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Due diligence: {self.company_name}"


class AnalysisReport(models.Model):
    """
    A generated due-diligence report: executive summary, risk assessment, and
    growth opportunities, all derived from retrieved chunks and grounded with
    citations back to the source documents.
    """

    session = models.ForeignKey(
        DueDiligenceSession, on_delete=models.CASCADE, related_name="reports"
    )
    executive_summary = models.TextField()
    risk_assessment = models.JSONField(default=list)  # [{title, severity, explanation}, ...]
    growth_opportunities = models.JSONField(default=list)  # [{title, explanation}, ...]
    raw_llm_response = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Report for {self.session.company_name} ({self.generated_at:%Y-%m-%d})"


class Citation(models.Model):
    """
    Links a specific claim made in a report (or an answer) back to the exact
    document chunk and page number it was derived from — this is what makes
    the output 'source-backed' rather than a black-box summary.
    """

    report = models.ForeignKey(
        AnalysisReport, on_delete=models.CASCADE, related_name="citations", null=True, blank=True
    )
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="citations", null=True, blank=True
    )
    chunk = models.ForeignKey("documents.DocumentChunk", on_delete=models.CASCADE)
    claim_excerpt = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"Citation -> {self.chunk.document.title} p.{self.chunk.page_number}"


class Question(models.Model):
    """An interactive Q&A turn against a session's document set."""

    session = models.ForeignKey(
        DueDiligenceSession, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    answer_text = models.TextField(blank=True)
    asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["asked_at"]

    def __str__(self):
        return self.question_text[:60]
