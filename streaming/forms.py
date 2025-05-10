from django import forms

class ScrapingForm(forms.Form):
    url = forms.URLField(label='Link', max_length=200, required=True)
