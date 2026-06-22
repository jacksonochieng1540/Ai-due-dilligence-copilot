from rest_framework import serializers

from .models import Document, DocumentChunk


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ["id", "chunk_index", "page_number", "content", "token_count"]


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "company_name",
            "title",
            "document_type",
            "file",
            "status",
            "processing_error",
            "page_count",
            "chunk_count",
            "uploaded_at",
            "processed_at",
        ]
        read_only_fields = ["status", "processing_error", "page_count", "processed_at"]


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "company_name", "title", "document_type", "file"]
