# passwordmanager/models.py
from django.db import models
from django.contrib.auth.models import User

class VaultEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    site_name = models.CharField(max_length=255, db_index=True)
    url = models.URLField(blank=True)
    username = models.CharField(max_length=255, db_index=True)
    encrypted_password = models.BinaryField()
    nonce = models.BinaryField()
    salt = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'site_name']),
            models.Index(fields=['user', 'site_name', 'username']),
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']
