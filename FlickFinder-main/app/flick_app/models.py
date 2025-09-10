# models.py
from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=255, unique=True, default=-1)  # Unique identifier for the user
    preferences = models.TextField()  # Field to store the movie preferences

    def __str__(self):
        return self.user_id
