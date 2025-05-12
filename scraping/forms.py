# streaming/forms.py

from django import forms
from urllib.parse import urlparse

class ScrapingForm(forms.Form):
    link = forms.URLField(label='Torrent page URL', max_length=500, required=True)

    # Only these domains are allowed:
    WHITELIST = {
        '1337x.to',
        'nyaa.si',
        'thepiratebay.org',
    }

    def clean_link(self):
        url = self.cleaned_data['link']
        domain = urlparse(url).netloc.lower()

        # strip any port (e.g. example.com:8080 → example.com)
        if ':' in domain:
            domain = domain.split(':', 1)[0]

        if domain not in self.WHITELIST:
            raise forms.ValidationError(
                f"Domain '{domain}' is not allowed. "
                f"Please use one of: {', '.join(self.WHITELIST)}."
            )
        return url
