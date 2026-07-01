from django.conf import settings
from django.db import models


class Document(models.Model):
    """
    A single uploaded source file: a 10-K filing, a balance sheet, an investor
    deck, a market report, etc. One due-diligence session can reference many
    Documents belonging to the same target company.
    """

    class DocumentType(models.TextChoices):
        FILING = "filing", "Regulatory Filing"
        FINANCIAL_STATEMENT = "financial_statement", "Financial Statement"
        INVESTOR_PRESENTATION = "investor_presentation", "Investor Presentation"
        MARKET_REPORT = "market_report", "Market Report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents"
    )
    company_name = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=32, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    file = models.FileField(upload_to="due_diligence/%Y/%m/")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    processing_error = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.company_name} — {self.title}"


class DocumentChunk(models.Model):
    """
    A single retrievable passage of a Document, with its embedding vector
    stored directly in Postgres via pgvector. This is what gets searched
    during retrieval.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    # embedding field removed for SQLite compatibility
    # embedding = VectorField(dimensions=1536, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document_id", "chunk_index"]

    def __str__(self):
        return f"{self.document.title} [chunk {self.chunk_index}]"
