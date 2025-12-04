from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class LoginCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    telegram_id = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
