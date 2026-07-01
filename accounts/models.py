from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    organization = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
