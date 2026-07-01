from django.utils import timezone

from ..models import Document


def index_document(document: Document) -> None:
    """
    Process a document: extract text, chunk it, and generate embeddings.
    
    This is a stub implementation. The actual implementation would:
    1. Extract text from the uploaded file (PDF, DOCX, etc.)
    2. Split text into chunks
    3. Generate embeddings for each chunk
    4. Store chunks with embeddings in DocumentChunk model
    
    For now, this just marks the document as ready.
    """
    document.status = Document.Status.READY
    document.processed_at = timezone.now()
    document.save()
