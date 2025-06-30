# passwordmanager/forms.py
from django import forms

class VaultEntryForm(forms.Form):
    site_name = forms.CharField()
    url = forms.URLField(required=False)
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    master_password = forms.CharField(widget=forms.PasswordInput)
