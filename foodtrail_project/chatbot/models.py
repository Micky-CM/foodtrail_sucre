from django.db import models
from django.contrib.auth.models import User
from establishments.models import Establishment

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SesiÃ³n {self.session_id} - {self.created_at}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'Usuario'),
        ('bot', 'Bot'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    recommended_establishments = models.ManyToManyField(Establishment, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, null=True, blank=True)
    preferred_cuisine_types = models.JSONField(default=list)
    preferred_meal_times = models.JSONField(default=list)
    preferred_ambience = models.JSONField(default=list)
    budget_range = models.CharField(max_length=50, blank=True)
    dietary_restrictions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        user_info = self.user.username if self.user else f"SesiÃ³n {self.session.session_id}"
        return f"Preferencias de {user_info}"
