from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentUploadForm
from .models import Document
from .services.vectorstore import index_document


@login_required
def upload_document(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            try:
                index_document(document)
            except Exception:
                pass
            return redirect("documents:list")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload.html", {"form": form})


@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user)
    return render(request, "documents/list.html", {"documents": documents})


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    chunks = document.chunks.all()[:20] 
    return render(
        request, "documents/detail.html", {"document": document, "chunks": chunks}
    )
