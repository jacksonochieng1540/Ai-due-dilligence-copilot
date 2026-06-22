from django import forms

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["company_name", "title", "document_type", "file"]
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "e.g. Safaricom PLC"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. FY2025 Annual Report"}),
        }
