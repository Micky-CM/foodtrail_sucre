from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
import logging
from datetime import datetime

from .models import ChatSession, ChatMessage, UserPreference
from .llm_client import OllamaClient
from .recommendation_engine import RecommendationEngine
from .neural_network import NeuralNetworkClassifier

logger = logging.getLogger(__name__)

class ChatBotView(View):
    """Vista principal del chatbot"""
    
    def __init__(self):
        super().__init__()
        self.ollama_client = OllamaClient()
        self.recommendation_engine = RecommendationEngine()
        self.neural_classifier = NeuralNetworkClassifier()
    
    def get(self, request):
        """Renderiza la página del chat"""
        return render(request, 'chatbot/chat.html')
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Procesa mensajes del chat"""
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            
            if not user_message:
                return JsonResponse({
                    'error': 'Mensaje vacío'
                }, status=400)
            
            # Obtener o crear sesión
            session = self._get_or_create_session(session_id, request)
            
            # Guardar mensaje del usuario
            user_chat_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message
            )
            
            # Procesar mensaje y generar respuesta
            response_data = self._process_user_message(user_message, session)
            
            # Guardar respuesta del bot
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=response_data['message']
            )
            
            # Si hay recomendaciones, asociarlas al mensaje
            if response_data.get('recommendations'):
                from establishments.models import Establishment
                for rec in response_data['recommendations']:
                    try:
                        establishment = Establishment.objects.get(id=rec['id'])
                        bot_message.recommended_establishments.add(establishment)
                    except Establishment.DoesNotExist:
                        pass
            
            return JsonResponse({
                'message': response_data['message'],
                'recommendations': response_data.get('recommendations', []),
                'session_id': session.session_id,
                'intent': response_data.get('intent', ''),
                'confidence': response_data.get('confidence', 0.0)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)
    
    def _get_or_create_session(self, session_id: str, request) -> ChatSession:
        """Obtiene o crea una sesión de chat"""
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id)
                return session
            except ChatSession.DoesNotExist:
                pass
        
        # Crear nueva sesión
        new_session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            session_id=new_session_id,
            user=request.user if request.user.is_authenticated else None
        )
        
        return session
    
    def _process_user_message(self, user_message: str, session: ChatSession) -> dict:
        """Procesa el mensaje del usuario y genera respuesta"""
        
        # 1. Analizar mensaje con la red neuronal
        analysis = self.neural_classifier.analyze_message(user_message)
        intent = analysis['intent']
        confidence = analysis['confidence']
        features = analysis['features']
        
        logger.info(f"Análisis del mensaje - Intent: {intent}, Confidence: {confidence}")
        
        # 2. Obtener contexto de la conversación
        context = self._get_conversation_context(session)
        
        # 3. Determinar si necesitamos buscar establecimientos
        recommendations = []
        
        if self.neural_classifier.should_search_establishments(intent) or confidence < 0.7:
            # Usar LLM para extraer preferencias más detalladas
            preferences = self.ollama_client.extract_preferences(user_message)
            
            # Si no se extrajeron preferencias con LLM, usar las del análisis neural
            if not preferences:
                preferences = self._convert_features_to_preferences(features, analysis.get('entities', {}))
            
            logger.info(f"Preferencias extraídas: {preferences}")
            
            # Buscar establecimientos
            if preferences:
                recommendations = self.recommendation_engine.find_establishments(preferences, user_message)
                
                # Actualizar preferencias del usuario
                self._update_user_preferences(session, preferences)
        
        # 4. Generar respuesta usando LLM
        if recommendations:
            response_message = self.ollama_client.generate_recommendation_text(recommendations, user_message)
        else:
            # Respuesta conversacional sin recomendaciones específicas
            if intent == 'saludo':
                response_message = "¡Hola! Soy FoodTrail AI, tu asistente gastronómico especializado en Sucre. Estoy aquí para recomendarte los mejores lugares para comer. ¿Qué tipo de experiencia culinaria buscas hoy?"
            elif intent == 'agradecimiento':
                response_message = "¡Es un placer ayudarte! Si necesitas más recomendaciones o tienes preguntas específicas sobre algún restaurante, estaré aquí para ayudarte."
            else:
                # Usar LLM para respuesta general
                template = self.neural_classifier.get_response_template(intent)
                response_message = self.ollama_client.generate_response(user_message, context)
                
                if not response_message or "error" in response_message.lower():
                    response_message = template
        
        return {
            'message': response_message,
            'recommendations': recommendations,
            'intent': intent,
            'confidence': confidence
        }
    
    def _get_conversation_context(self, session: ChatSession) -> str:
        """Obtiene el contexto de los últimos mensajes de la conversación"""
        recent_messages = ChatMessage.objects.filter(
            session=session
        ).order_by('-timestamp')[:6]  # Últimos 6 mensajes
        
        context_parts = []
        for msg in reversed(recent_messages):
            role = "Usuario" if msg.message_type == 'user' else "FoodTrail AI"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def _convert_features_to_preferences(self, features: dict, entities: dict) -> dict:
        """Convierte características y entidades extraídas a formato de preferencias"""
        preferences = {}
        
        # Mapear características a preferencias
        if 'tiempo_comida' in features:
            preferences['horario_comida'] = features['tiempo_comida']
        
        if 'grupo_size' in features:
            group_size = features['grupo_size'][0] if features['grupo_size'] else None
            if group_size in ['pareja']:
                preferences['ambiente'] = ['romantico', 'intimo']
            elif group_size in ['grupo_grande']:
                preferences['ambiente'] = ['familiar', 'amplio']
        
        if 'presupuesto' in features:
            preferences['presupuesto'] = features['presupuesto']
        
        # Procesar entidades
        if 'platos_tipicos' in entities:
            preferences['tipo_comida'] = ['tradicional', 'boliviana']
        
        if 'zonas' in entities:
            preferences['zona'] = entities['zonas']
        
        return preferences
    
    def _update_user_preferences(self, session: ChatSession, preferences: dict):
        """Actualiza las preferencias del usuario en la base de datos"""
        try:
            user_pref, created = UserPreference.objects.get_or_create(
                session=session,
                defaults={
                    'user': session.user if session.user else None
                }
            )
            
            # Actualizar preferencias existentes
            for pref_type, values in preferences.items():
                if pref_type == 'tipo_establecimiento':
                    current = user_pref.preferred_cuisine_types or []
                    user_pref.preferred_cuisine_types = list(set(current + values))
                elif pref_type == 'horario_comida':
                    current = user_pref.preferred_meal_times or []
                    user_pref.preferred_meal_times = list(set(current + values))
                elif pref_type == 'ambiente':
                    current = user_pref.preferred_ambience or []
                    user_pref.preferred_ambience = list(set(current + values))
                elif pref_type == 'presupuesto':
                    user_pref.budget_range = values[0] if values else user_pref.budget_range
            
            user_pref.save()
            
        except Exception as e:
            logger.error(f"Error actualizando preferencias: {e}")

@require_http_methods(["GET"])
def chat_history(request, session_id):
    """Obtiene el historial de una sesión de chat"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        
        history = []
        for msg in messages:
            message_data = {
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            
            # Incluir recomendaciones si las hay
            if msg.message_type == 'bot' and msg.recommended_establishments.exists():
                recommendations = []
                for est in msg.recommended_establishments.all():
                    recommendations.append({
                        'id': est.id,
                        'name': est.name,
                        'description': est.description,
                        'zone': est.zone
                    })
                message_data['recommendations'] = recommendations
            
            history.append(message_data)
        
        return JsonResponse({
            'session_id': session_id,
            'messages': history
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'error': 'Sesión no encontrada'
        }, status=404)

@require_http_methods(["GET"])
def health_check(request):
    """Verifica el estado del sistema de chatbot"""
    ollama_client = OllamaClient()
    
    return JsonResponse({
        'status': 'ok',
        'ollama_connected': ollama_client.check_connection(),
        'timestamp': datetime.now().isoformat()
    })
