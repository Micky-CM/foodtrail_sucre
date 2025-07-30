from django.contrib import admin
from .models import ChatSession, ChatMessage, UserPreference

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'user')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'NÃºmero de mensajes'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'content_preview', 'timestamp', 'has_recommendations')
    list_filter = ('message_type', 'timestamp', 'session')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('timestamp',)
    filter_horizontal = ('recommended_establishments',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'
    
    def has_recommendations(self, obj):
        return obj.recommended_establishments.exists()
    has_recommendations.boolean = True
    has_recommendations.short_description = 'Tiene recomendaciones'

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'session', 'cuisine_count', 'budget_range', 'updated_at')
    list_filter = ('budget_range', 'created_at', 'updated_at')
    search_fields = ('user__username', 'session__session_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def user_display(self, obj):
        return obj.user.username if obj.user else f"SesiÃ³n {obj.session.session_id}"
    user_display.short_description = 'Usuario'
    
    def cuisine_count(self, obj):
        return len(obj.preferred_cuisine_types) if obj.preferred_cuisine_types else 0
    cuisine_count.short_description = 'Tipos de cocina'
