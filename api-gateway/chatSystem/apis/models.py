from django.db import models


class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    language = models.CharField(max_length=10, default="en")

    def __str__(self):
        return self.username


class ChatMessage(models.Model):
    MESSAGE_TYPE = (
        ("text", "Text"),
        ("audio", "Audio"),
    )

    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE)
    original_message = models.TextField(null=True, blank=True)
    translated_message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}"
