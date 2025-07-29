"""
Cliente para usar APIs de LLM en línea (Groq, OpenAI, etc.)
Reemplaza la dependencia local de Ollama
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class OnlineLLMClient:
    """Cliente para interactuar con APIs de LLM en línea"""
    
    def __init__(self, provider: str = "groq", api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.session = requests.Session()
        
        # Configuraciones por proveedor
        if self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = "llama3-8b-8192"  # Modelo gratuito de Groq
        elif self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            self.model = "gpt-3.5-turbo"
        else:
            # Fallback a simulación si no hay API key
            self.provider = "fallback"
            self.model = "fallback"
    
    def _get_api_key(self) -> str:
        """Obtiene la API key de las variables de entorno"""
        if self.provider == "groq":
            return os.getenv('GROQ_API_KEY', '')
        elif self.provider == "openai":
            return os.getenv('OPENAI_API_KEY', '')
        return ''
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 500) -> str:
        """
        Genera una respuesta usando la API del LLM
        
        Args:
            prompt: El prompt del usuario
            context: Contexto adicional para la conversación
            max_tokens: Número máximo de tokens en la respuesta
            
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            if self.provider == "fallback":
                return self._fallback_response(prompt)
            
            # Construir el prompt completo con contexto
            full_prompt = self._build_prompt(prompt, context)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions", 
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Error API {self.provider}: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
            
        except Exception as e:
            logger.error(f"Error conectando con {self.provider}: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Respuesta de respaldo cuando no hay API disponible"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['hola', 'buenos', 'buenas', 'saludos']):
            return "¡Hola! Soy FoodTrail AI, tu asistente gastronómico especializado en Sucre. Estoy aquí para recomendarte los mejores lugares para comer. ¿Qué tipo de experiencia culinaria buscas hoy?"
        
        elif any(word in prompt_lower for word in ['gracias', 'muchas gracias', 'perfecto']):
            return "¡Es un placer ayudarte! Si necesitas más recomendaciones o tienes preguntas específicas sobre algún restaurante, estaré aquí para ayudarte."
        
        elif any(word in prompt_lower for word in ['romántico', 'pareja', 'cita', 'novio', 'novia']):
            return "Te recomiendo lugares con ambiente romántico perfecto para una cita especial. Buscaré restaurantes con mesas privadas, música suave y decoración acogedora en Sucre."
        
        elif any(word in prompt_lower for word in ['familia', 'familiar', 'niños', 'hijos']):
            return "Perfecto para una salida familiar. Te buscaré restaurantes amplios, con ambiente tranquilo y menús que gusten tanto a adultos como a niños."
        
        elif any(word in prompt_lower for word in ['tradicional', 'boliviana', 'típica', 'local']):
            return "¡Excelente elección! Sucre tiene una rica tradición gastronómica. Te recomendaré lugares donde puedas disfrutar auténtica comida chuquisaqueña y boliviana."
        
        else:
            return "Entiendo que buscas recomendaciones gastronómicas en Sucre. Te ayudaré a encontrar el lugar perfecto según tus preferencias. ¿Podrías contarme más detalles sobre qué tipo de ambiente o comida prefieres?"
    
    def _build_prompt(self, user_prompt: str, context: str = "") -> str:
        """Construye el prompt completo con instrucciones del sistema"""
        
        system_prompt = """Eres FoodTrail AI, un asistente especializado en recomendar restaurantes y lugares gastronómicos en Sucre, Bolivia. 

Tu personalidad:
- Eres amigable, conocedor y entusiasta sobre la gastronomía local
- Hablas en español de manera natural y cercana
- Eres especialista en la comida boliviana y chuquisaqueña
- Siempre tratas de entender las preferencias específicas del usuario

Tus tareas principales:
1. Interpretar las solicitudes del usuario sobre lugares para comer
2. Extraer información clave como: tipo de comida, ambiente deseado, ocasión, presupuesto, horario
3. Recomendar establecimientos basándote en la información de la base de datos
4. Proporcionar descripciones atractivas y útiles de los lugares

Reglas importantes:
- Siempre responde en español
- Sé específico sobre por qué recomiendas un lugar
- Si necesitas más información, haz preguntas específicas
- Mantén un tono conversacional y amigable
- Si no tienes información suficiente, admítelo honestamente
- Mantén las respuestas concisas pero informativas

"""
        
        if context:
            full_prompt = f"{system_prompt}\n\nContexto de la conversación:\n{context}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
        else:
            full_prompt = f"{system_prompt}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
            
        return full_prompt
    
    def extract_preferences(self, user_message: str) -> Dict[str, Any]:
        """
        Extrae preferencias del mensaje del usuario usando IA
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Dict con las preferencias extraídas
        """
        if self.provider == "fallback":
            return self._extract_preferences_fallback(user_message)
        
        extraction_prompt = f"""
Analiza el siguiente mensaje de un usuario que busca recomendaciones de restaurantes y extrae la información en formato JSON.

Mensaje del usuario: "{user_message}"

Extrae la siguiente información y devuelve SOLO un JSON válido (sin texto adicional):

{{
    "tipo_establecimiento": ["restaurante", "cafeteria", "pub"],
    "tipo_comida": ["tradicional", "moderna", "italiana"],
    "horario_comida": ["desayuno", "almuerzo", "cena"],
    "ambiente": ["romantico", "familiar", "tranquilo"],
    "ocasion": ["cita", "familia", "negocios"],
    "presupuesto": ["economico", "medio", "alto"],
    "caracteristicas": ["wifi", "parking", "terraza"]
}}

Solo incluye valores si están claramente mencionados o implícitos en el mensaje.
"""
        
        try:
            response = self.generate_response(extraction_prompt, max_tokens=200)
            
            # Intentar extraer JSON de la respuesta
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return self._extract_preferences_fallback(user_message)
                
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error extrayendo preferencias: {e}")
            return self._extract_preferences_fallback(user_message)
    
    def _extract_preferences_fallback(self, user_message: str) -> Dict[str, Any]:
        """Extracción de preferencias básica sin API"""
        preferences = {}
        message_lower = user_message.lower()
        
        # Tipo de establecimiento
        if any(word in message_lower for word in ['restaurante', 'restaurant']):
            preferences['tipo_establecimiento'] = ['restaurante']
        elif any(word in message_lower for word in ['café', 'cafeteria', 'coffee']):
            preferences['tipo_establecimiento'] = ['cafeteria']
        
        # Tipo de comida
        if any(word in message_lower for word in ['tradicional', 'típica', 'boliviana', 'local']):
            preferences['tipo_comida'] = ['tradicional']
        elif any(word in message_lower for word in ['italiana', 'pizza', 'pasta']):
            preferences['tipo_comida'] = ['italiana']
        
        # Horario
        if any(word in message_lower for word in ['desayuno', 'mañana', 'breakfast']):
            preferences['horario_comida'] = ['desayuno']
        elif any(word in message_lower for word in ['almuerzo', 'almorzar', 'mediodía']):
            preferences['horario_comida'] = ['almuerzo']
        elif any(word in message_lower for word in ['cena', 'cenar', 'noche']):
            preferences['horario_comida'] = ['cena']
        
        # Ambiente
        if any(word in message_lower for word in ['romántico', 'pareja', 'cita', 'íntimo']):
            preferences['ambiente'] = ['romantico']
        elif any(word in message_lower for word in ['familiar', 'familia', 'niños']):
            preferences['ambiente'] = ['familiar']
        elif any(word in message_lower for word in ['tranquilo', 'silencioso', 'relajado']):
            preferences['ambiente'] = ['tranquilo']
        
        # Ocasión
        if any(word in message_lower for word in ['cita', 'date', 'romántico']):
            preferences['ocasion'] = ['cita']
        elif any(word in message_lower for word in ['familia', 'familiar', 'niños']):
            preferences['ocasion'] = ['familia']
        elif any(word in message_lower for word in ['trabajo', 'negocios', 'reunión']):
            preferences['ocasion'] = ['negocios']
        
        return preferences
    
    def generate_recommendation_text(self, establishments: List[Dict], user_query: str) -> str:
        """
        Genera texto de recomendación personalizado basado en los establecimientos encontrados
        
        Args:
            establishments: Lista de establecimientos con su información
            user_query: La consulta original del usuario
            
        Returns:
            str: Texto de recomendación personalizado
        """
        if not establishments:
            return "No encontré establecimientos que coincidan exactamente con tus preferencias, pero te recomiendo explorar las opciones disponibles en el centro de Sucre donde hay gran variedad de restaurantes."
        
        if self.provider == "fallback":
            return self._generate_recommendation_fallback(establishments, user_query)
        
        # Preparar información de establecimientos para el prompt
        establishments_info = []
        for est in establishments:
            info = f"- {est['name']} (Zona: {est['zone']}): {est['description']}"
            if est.get('establishment_types'):
                info += f" - Tipos: {', '.join(est['establishment_types'])}"
            if est.get('phone'):
                info += f" - Teléfono: {est['phone']}"
            establishments_info.append(info)
        
        establishments_text = "\n".join(establishments_info)
        
        recommendation_prompt = f"""
Basándote en la consulta del usuario y el establecimiento disponible, genera una recomendación personalizada y concisa.

Consulta del usuario: "{user_query}"

Establecimiento recomendado:
{establishments_text}

Instrucciones:
1. Recomienda únicamente este establecimiento de forma entusiasta
2. Explica en máximo 3 líneas por qué es perfecto para lo que busca
3. Menciona 2-3 detalles relevantes (ubicación, ambiente, especialidad)
4. Incluye información de contacto (zona y teléfono)
5. Usa un tono amigable pero conciso
6. Termina con una pregunta breve para continuar la conversación

Genera una recomendación breve y atractiva:
"""

        return self.generate_response(recommendation_prompt, max_tokens=300)
    
    def _generate_recommendation_fallback(self, establishments: List[Dict], user_query: str) -> str:
        """Genera recomendación básica sin API"""
        if establishments:
            est = establishments[0]  # Solo usar el primero
            return f"Te recomiendo **{est['name']}** en {est['zone']}. {est['description'][:100]}... Es perfecto para lo que buscas. ¿Te gustaría más información?"
        
        return "Encontré varias opciones interesantes para ti. ¿Te gustaría que te dé más detalles sobre alguna en particular?"
    
    def check_connection(self) -> bool:
        """Verifica si la API está disponible"""
        if self.provider == "fallback":
            return True
            
        try:
            test_response = self.generate_response("test", max_tokens=10)
            return "error" not in test_response.lower()
        except:
            return False
