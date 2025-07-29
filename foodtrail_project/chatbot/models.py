from django.db import models
from django.contrib.auth.models import User
from establishments.models import Establishment

class ChatSession(models.Model):
    """Modelo para gestionar sesiones de chat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Sesión {self.session_id} - {self.created_at}"

class ChatMessage(models.Model):
    """Modelo para almacenar mensajes del chat"""
    MESSAGE_TYPES = [
        ('user', 'Usuario'),
        ('bot', 'Bot'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Para recomendaciones específicas
    recommended_establishments = models.ManyToManyField(Establishment, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class UserPreference(models.Model):
    """Modelo para almacenar preferencias del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Preferencias detectadas por la IA
    preferred_cuisine_types = models.JSONField(default=list)  # ['tradicional', 'moderna', etc.]
    preferred_meal_times = models.JSONField(default=list)    # ['desayuno', 'almuerzo', etc.]
    preferred_ambience = models.JSONField(default=list)      # ['romántico', 'familiar', etc.]
    budget_range = models.CharField(max_length=50, blank=True)
    dietary_restrictions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Sesión {self.session.session_id}"
        return f"Preferencias de {user_info}"
