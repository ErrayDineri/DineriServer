from django import forms

class ScrapingForm(forms.Form):
    link = forms.CharField(required=False)  # URL input (optional)
    search_term = forms.CharField(required=False)  # Search term input (optional)
