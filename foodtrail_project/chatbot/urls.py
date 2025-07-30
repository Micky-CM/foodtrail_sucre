from django.urls import path
from . import views_api

app_name = 'chatbot'

urlpatterns = [
    path('', views_api.chat_page, name='chat'),
    
    path('api/message/', views_api.chat_api, name='chat_api'),
    path('api/history/<str:session_id>/', views_api.chat_history, name='chat_history'),
    path('api/health/', views_api.health_check, name='health_check'),
]
