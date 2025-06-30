# passwordmanager/models.py
from django.db import models
from django.contrib.auth.models import User

class VaultEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    username = models.CharField(max_length=255)
    encrypted_password = models.BinaryField()
    nonce = models.BinaryField()
    salt = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
