from django import forms
from .models import StudyMaterial

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = [
            'title', 'description', 'class_name', 'subject', 'chapter', 'unit',
            'keywords', 'pdf_file', 'thumbnail', 'visibility', 'download_permission',
            'status', 'featured'
        ]

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files (.pdf) are allowed!")
            # 50MB limit
            if pdf.size > 50 * 1024 * 1024:
                raise forms.ValidationError("File size exceeds maximum allowed limit of 50 MB.")
        return pdf
