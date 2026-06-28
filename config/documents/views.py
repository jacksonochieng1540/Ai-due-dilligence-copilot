from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services.vectorstore import index_document


class DocumentViewSet(viewsets.ModelViewSet):
    """
    CRUD + processing endpoint for uploaded due-diligence source documents.

    POST   /api/documents/                -> upload a new file
    GET    /api/documents/                -> list your documents
    GET    /api/documents/{id}/           -> retrieve one
    POST   /api/documents/{id}/process/   -> run extraction+chunking+embedding
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentUploadSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        document = self.get_object()
        try:
            index_document(document)
        except Exception as exc:
            return Response(
                {"detail": f"Processing failed: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(DocumentSerializer(document).data, status=status.HTTP_200_OK)
