# passwordmanager/forms.py
from django import forms

class VaultEntryForm(forms.Form):
    site_name = forms.CharField()
    url = forms.URLField(required=False)
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    master_password = forms.CharField(widget=forms.PasswordInput)


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file with password data (Bitwarden format supported)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    master_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Master Password",
        help_text="Enter your master password to encrypt imported passwords"
    )
    allow_duplicates = forms.BooleanField(
        required=False,
        initial=True,
        label="Allow Duplicates",
        help_text="Import entries even if they already exist in your vault",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
