from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import json
import uuid
import logging
from datetime import datetime

from .models import ChatSession, ChatMessage, UserPreference
from .online_llm_client import OnlineLLMClient
from .recommendation_engine import RecommendationEngine
from .neural_network import NeuralNetworkClassifier

logger = logging.getLogger(__name__)

def chat_page(request):
    """Renderiza la página del chat"""
    return render(request, 'chatbot/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint para procesar mensajes del chat"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        if not user_message:
            return JsonResponse({
                'error': 'Mensaje vacío'
            }, status=400)
        
        # Inicializar componentes
        llm_client = OnlineLLMClient()
        recommendation_engine = RecommendationEngine()
        neural_classifier = NeuralNetworkClassifier()
        
        # Obtener o crear sesión
        session = get_or_create_session(session_id, request)
        
        # Guardar mensaje del usuario
        user_chat_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=user_message
        )
        
        # Procesar mensaje y generar respuesta
        response_data = process_user_message(
            user_message, session, llm_client, 
            recommendation_engine, neural_classifier
        )
        
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
        print(f"🔥 ERROR en chat_api: {e}")
        return JsonResponse({
            'message': 'Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo.',
            'error': 'Error interno del servidor'
        }, status=500)

def get_or_create_session(session_id: str, request) -> ChatSession:
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

def process_user_message(user_message: str, session: ChatSession, 
                        llm_client, recommendation_engine, neural_classifier) -> dict:
    """Procesa el mensaje del usuario y genera respuesta"""
    
    print(f"🔍 Procesando mensaje: {user_message}")
    
    # 1. Analizar mensaje con la red neuronal
    print("🧠 Analizando con red neuronal...")
    analysis = neural_classifier.analyze_message(user_message)
    intent = analysis['intent']
    confidence = analysis['confidence']
    features = analysis['features']
    
    print(f"✅ Análisis completado - Intent: {intent}, Confidence: {confidence}")
    logger.info(f"Análisis del mensaje - Intent: {intent}, Confidence: {confidence}")
    
    # 2. Obtener contexto de la conversación
    print("📝 Obteniendo contexto...")
    context = get_conversation_context(session)
    
    # 3. Determinar si necesitamos buscar establecimientos
    recommendations = []
    
    try:
        # Solo buscar establecimientos si la intención es relevante Y tiene suficiente confianza
        should_search = (
            neural_classifier.should_search_establishments(intent) and 
            confidence > 0.3  # Umbral mínimo de confianza
        ) or (
            # O si la confianza es baja pero hay palabras clave de búsqueda
            confidence < 0.5 and any(keyword in user_message.lower() 
                                   for keyword in ['restaurante', 'lugar', 'comer', 'comida', 'recomienda', 'quiero', 'busco'])
        )
        
        if should_search:
            print("🔍 Buscando establecimientos...")
            # Usar LLM para extraer preferencias más detalladas
            preferences = llm_client.extract_preferences(user_message)
            print(f"✅ Preferencias extraídas por LLM: {preferences}")
            
            # Si no se extrajeron preferencias con LLM, usar las del análisis neural
            if not preferences:
                preferences = convert_features_to_preferences(features, analysis.get('entities', {}))
            
            logger.info(f"Preferencias extraídas: {preferences}")
            
            # Buscar establecimientos
            if preferences:
                recommendations = recommendation_engine.find_establishments(preferences, user_message)
                print(f"✅ Encontradas {len(recommendations)} recomendaciones")
                
                # Actualizar preferencias del usuario
                update_user_preferences(session, preferences)
        
        # 4. Generar respuesta usando LLM
        print("🤖 Generando respuesta con LLM...")
        if recommendations:
            response_message = llm_client.generate_recommendation_text(recommendations, user_message)
        else:
            # Respuesta conversacional sin recomendaciones específicas
            if intent == 'saludo':
                response_message = "¡Hola! Soy FoodTrail AI, tu asistente gastronómico especializado en Sucre. Estoy aquí para recomendarte los mejores lugares para comer. ¿Qué tipo de experiencia culinaria buscas hoy?"
            elif intent == 'agradecimiento':
                response_message = "¡Es un placer ayudarte! Si necesitas más recomendaciones o tienes preguntas específicas sobre algún restaurante, estaré aquí para ayudarte."
            else:
                # Usar LLM para respuesta general
                template = neural_classifier.get_response_template(intent)
                response_message = llm_client.generate_response(user_message, context)
                
                if not response_message or "error" in response_message.lower():
                    response_message = template
        
        print(f"✅ Respuesta generada: {response_message[:100]}...")
        
        return {
            'message': response_message,
            'recommendations': recommendations,
            'intent': intent,
            'confidence': confidence
        }
        
    except Exception as e:
        print(f"🔥 ERROR en process_user_message: {e}")
        logger.error(f"Error en process_user_message: {e}")
        return {
            'message': 'Lo siento, ocurrió un error procesando tu mensaje.',
            'recommendations': [],
            'intent': 'error',
            'confidence': 0.0
        }

def get_conversation_context(session: ChatSession) -> str:
    """Obtiene el contexto de los últimos mensajes de la conversación"""
    recent_messages = ChatMessage.objects.filter(
        session=session
    ).order_by('-timestamp')[:6]  # Últimos 6 mensajes
    
    context_parts = []
    for msg in reversed(recent_messages):
        role = "Usuario" if msg.message_type == 'user' else "FoodTrail AI"
        context_parts.append(f"{role}: {msg.content}")
    
    return "\n".join(context_parts)

def convert_features_to_preferences(features: dict, entities: dict) -> dict:
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

def update_user_preferences(session: ChatSession, preferences: dict):
    """Actualiza las preferencias del usuario en la base de datos"""
    try:
        user_pref, created = UserPreference.objects.get_or_create(
            session=session,
            defaults={
                'user': session.user if session.user else None
            }
        )
        
        # Función auxiliar para normalizar valores
        def normalize_values(values):
            if isinstance(values, dict):
                # Extraer claves donde el valor es True
                return [k for k, v in values.items() if v]
            elif isinstance(values, list):
                return values
            else:
                return [values] if values else []
        
        # Actualizar preferencias existentes
        for pref_type, values in preferences.items():
            normalized_values = normalize_values(values)
            
            if pref_type == 'tipo_establecimiento':
                current = user_pref.preferred_cuisine_types or []
                user_pref.preferred_cuisine_types = list(set(current + normalized_values))
            elif pref_type == 'horario_comida':
                current = user_pref.preferred_meal_times or []
                user_pref.preferred_meal_times = list(set(current + normalized_values))
            elif pref_type == 'ambiente':
                current = user_pref.preferred_ambience or []
                user_pref.preferred_ambience = list(set(current + normalized_values))
            elif pref_type == 'presupuesto':
                budget_values = normalize_values(values)
                user_pref.budget_range = budget_values[0] if budget_values else user_pref.budget_range
        
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
    llm_client = OnlineLLMClient()
    
    return JsonResponse({
        'status': 'ok',
        'llm_connected': llm_client.check_connection(),
        'provider': llm_client.provider,
        'model': llm_client.model,
        'timestamp': datetime.now().isoformat()
    })
