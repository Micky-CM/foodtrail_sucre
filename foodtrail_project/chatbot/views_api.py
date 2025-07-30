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
    return render(request, 'chatbot/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        if not user_message:
            return JsonResponse({
                'error': 'Mensaje vacÃ­o'
            }, status=400)
        
        llm_client = OnlineLLMClient()
        recommendation_engine = RecommendationEngine()
        neural_classifier = NeuralNetworkClassifier()
        
        session = get_or_create_session(session_id, request)
        
        user_chat_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=user_message
        )
        
        response_data = process_user_message(
            user_message, session, llm_client, 
            recommendation_engine, neural_classifier
        )
        
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=response_data['message']
        )
        
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
            'error': 'JSON invÃ¡lido'
        }, status=400)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        print(f"ðŸ”¥ ERROR en chat_api: {e}")
        return JsonResponse({
            'message': 'Lo siento, ocurriÃ³ un error inesperado. Por favor, intenta de nuevo.',
            'error': 'Error interno del servidor'
        }, status=500)

def get_or_create_session(session_id: str, request) -> ChatSession:
    if session_id:
        try:
            session = ChatSession.objects.get(session_id=session_id)
            return session
        except ChatSession.DoesNotExist:
            pass
    
    new_session_id = str(uuid.uuid4())
    session = ChatSession.objects.create(
        session_id=new_session_id,
        user=request.user if request.user.is_authenticated else None
    )
    
    return session

def process_user_message(user_message: str, session: ChatSession, 
                        llm_client, recommendation_engine, neural_classifier) -> dict:
    
    print(f"ðŸ” Procesando mensaje: {user_message}")
    
    print("ðŸ§  Analizando con red neuronal...")
    analysis = neural_classifier.analyze_message(user_message)
    intent = analysis['intent']
    confidence = analysis['confidence']
    features = analysis['features']
    
    print(f"âœ… AnÃ¡lisis completado - Intent: {intent}, Confidence: {confidence}")
    logger.info(f"AnÃ¡lisis del mensaje - Intent: {intent}, Confidence: {confidence}")
    
    print("ðŸ“ Obteniendo contexto...")
    context = get_conversation_context(session)
    
    recommendations = []
    
    try:
        should_search = (
            neural_classifier.should_search_establishments(intent) and 
            confidence > 0.3
        ) or (
            confidence < 0.5 and any(keyword in user_message.lower() 
                                   for keyword in ['restaurante', 'lugar', 'comer', 'comida', 'recomienda', 'quiero', 'busco'])
        )
        
        if should_search:
            print("ðŸ” Buscando establecimientos...")
            preferences = llm_client.extract_preferences(user_message)
            print(f"âœ… Preferencias extraÃ­das por LLM: {preferences}")
            
            if not preferences:
                preferences = convert_features_to_preferences(features, analysis.get('entities', {}))
            
            logger.info(f"Preferencias extraÃ­das: {preferences}")
            
            if preferences:
                recommendations = recommendation_engine.find_establishments(preferences, user_message)
                print(f"âœ… Encontradas {len(recommendations)} recomendaciones")
                
                update_user_preferences(session, preferences)
        
        print("ðŸ¤– Generando respuesta con LLM...")
        if recommendations:
            response_message = llm_client.generate_recommendation_text(recommendations, user_message)
        else:
            if intent == 'saludo':
                response_message = "Â¡Hola! Soy FoodTrail AI, tu asistente gastronÃ³mico especializado en Sucre. Estoy aquÃ­ para recomendarte los mejores lugares para comer. Â¿QuÃ© tipo de experiencia culinaria buscas hoy?"
            elif intent == 'agradecimiento':
                response_message = "Â¡Es un placer ayudarte! Si necesitas mÃ¡s recomendaciones o tienes preguntas especÃ­ficas sobre algÃºn restaurante, estarÃ© aquÃ­ para ayudarte."
            else:
                template = neural_classifier.get_response_template(intent)
                response_message = llm_client.generate_response(user_message, context)
                
                if not response_message or "error" in response_message.lower():
                    response_message = template
        
        print(f"âœ… Respuesta generada: {response_message[:100]}...")
        
        return {
            'message': response_message,
            'recommendations': recommendations,
            'intent': intent,
            'confidence': confidence
        }
        
    except Exception as e:
        print(f"ðŸ”¥ ERROR en process_user_message: {e}")
        logger.error(f"Error en process_user_message: {e}")
        return {
            'message': 'Lo siento, ocurriÃ³ un error procesando tu mensaje.',
            'recommendations': [],
            'intent': 'error',
            'confidence': 0.0
        }

def get_conversation_context(session: ChatSession) -> str:
    recent_messages = ChatMessage.objects.filter(
        session=session
    ).order_by('-timestamp')[:6]
    
    context_parts = []
    for msg in reversed(recent_messages):
        role = "Usuario" if msg.message_type == 'user' else "FoodTrail AI"
        context_parts.append(f"{role}: {msg.content}")
    
    return "\n".join(context_parts)

def convert_features_to_preferences(features: dict, entities: dict) -> dict:
    preferences = {}
    
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
    
    if 'platos_tipicos' in entities:
        preferences['tipo_comida'] = ['tradicional', 'boliviana']
    
    if 'zonas' in entities:
        preferences['zona'] = entities['zonas']
    
    return preferences

def update_user_preferences(session: ChatSession, preferences: dict):
    try:
        user_pref, created = UserPreference.objects.get_or_create(
            session=session,
            defaults={
                'user': session.user if session.user else None
            }
        )
        
        def normalize_values(values):
            if isinstance(values, dict):
                return [k for k, v in values.items() if v]
            elif isinstance(values, list):
                return values
            else:
                return [values] if values else []
        
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
            'error': 'SesiÃ³n no encontrada'
        }, status=404)

@require_http_methods(["GET"])
def health_check(request):
    llm_client = OnlineLLMClient()
    
    return JsonResponse({
        'status': 'ok',
        'llm_connected': llm_client.check_connection(),
        'provider': llm_client.provider,
        'model': llm_client.model,
        'timestamp': datetime.now().isoformat()
    })
