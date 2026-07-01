from django import forms

from .models import DueDiligenceSession


class SessionForm(forms.ModelForm):
    class Meta:
        model = DueDiligenceSession
        fields = ["company_name", "documents"]
        widgets = {
            "documents": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["documents"].queryset = self.fields["documents"].queryset.filter(
                owner=owner
            )
