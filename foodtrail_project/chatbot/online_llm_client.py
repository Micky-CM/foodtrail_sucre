
import requests
import json
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class OnlineLLMClient:
    
    def __init__(self, provider: str = "groq", api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.session = requests.Session()
        
        if self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = "llama3-8b-8192"
        elif self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            self.model = "gpt-3.5-turbo"
        else:
            self.provider = "fallback"
            self.model = "fallback"
    
    def _get_api_key(self) -> str:
        if self.provider == "groq":
            return os.getenv('GROQ_API_KEY', '')
        elif self.provider == "openai":
            return os.getenv('OPENAI_API_KEY', '')
        return ''
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 500) -> str:
        try:
            if self.provider == "fallback":
                return self._fallback_response(prompt)
            
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
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['hola', 'buenos', 'buenas', 'saludos']):
            return "Â¡Hola! Soy FoodTrail AI, tu asistente gastronÃ³mico especializado en Sucre. Estoy aquÃ­ para recomendarte los mejores lugares para comer. Â¿QuÃ© tipo de experiencia culinaria buscas hoy?"
        
        elif any(word in prompt_lower for word in ['gracias', 'muchas gracias', 'perfecto']):
            return "Â¡Es un placer ayudarte! Si necesitas mÃ¡s recomendaciones o tienes preguntas especÃ­ficas sobre algÃºn restaurante, estarÃ© aquÃ­ para ayudarte."
        
        elif any(word in prompt_lower for word in ['romÃ¡ntico', 'pareja', 'cita', 'novio', 'novia']):
            return "Te recomiendo lugares con ambiente romÃ¡ntico perfecto para una cita especial. BuscarÃ© restaurantes con mesas privadas, mÃºsica suave y decoraciÃ³n acogedora en Sucre."
        
        elif any(word in prompt_lower for word in ['familia', 'familiar', 'niÃ±os', 'hijos']):
            return "Perfecto para una salida familiar. Te buscarÃ© restaurantes amplios, con ambiente tranquilo y menÃºs que gusten tanto a adultos como a niÃ±os."
        
        elif any(word in prompt_lower for word in ['tradicional', 'boliviana', 'tÃ­pica', 'local']):
            return "Â¡Excelente elecciÃ³n! Sucre tiene una rica tradiciÃ³n gastronÃ³mica. Te recomendarÃ© lugares donde puedas disfrutar autÃ©ntica comida chuquisaqueÃ±a y boliviana."
        
        else:
            return "Entiendo que buscas recomendaciones gastronomicas en Sucre. Te ayudare a encontrar el lugar perfecto segun tus preferencias. Podrias contarme mas detalles sobre que tipo de ambiente o comida prefieres?"
    
    def _build_prompt(self, user_prompt: str, context: str = "") -> str:
        system_prompt = "Eres FoodTrail AI, un asistente especializado en recomendar restaurantes y lugares gastronomicos en Sucre, Bolivia. Eres amigable, conocedor y entusiasta sobre la gastronomia local. Hablas en espanol de manera natural y cercana."
        
        if context:
            full_prompt = f"{system_prompt}\n\nContexto de la conversacion:\n{context}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
        else:
            full_prompt = f"{system_prompt}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
            
        return full_prompt
    
    def extract_preferences(self, user_message: str) -> Dict[str, Any]:
        if self.provider == "fallback":
            return self._extract_preferences_fallback(user_message)
        
        extraction_prompt = f"Analiza el siguiente mensaje de un usuario que busca recomendaciones de restaurantes y extrae la informacion en formato JSON. Mensaje del usuario: {user_message}. Extrae la siguiente informacion y devuelve SOLO un JSON valido (sin texto adicional): tipo_establecimiento, tipo_comida, horario_comida, ambiente, ocasion, presupuesto, caracteristicas. Solo incluye valores si estan claramente mencionados o implicitos en el mensaje."
        
        try:
            response = self.generate_response(extraction_prompt, max_tokens=200)
            
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
        preferences = {}
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['restaurante', 'restaurant']):
            preferences['tipo_establecimiento'] = ['restaurante']
        elif any(word in message_lower for word in ['cafÃ©', 'cafeteria', 'coffee']):
            preferences['tipo_establecimiento'] = ['cafeteria']
        
        if any(word in message_lower for word in ['tradicional', 'tÃ­pica', 'boliviana', 'local']):
            preferences['tipo_comida'] = ['tradicional']
        elif any(word in message_lower for word in ['italiana', 'pizza', 'pasta']):
            preferences['tipo_comida'] = ['italiana']
        
        if any(word in message_lower for word in ['desayuno', 'maÃ±ana', 'breakfast']):
            preferences['horario_comida'] = ['desayuno']
        elif any(word in message_lower for word in ['almuerzo', 'almorzar', 'mediodÃ­a']):
            preferences['horario_comida'] = ['almuerzo']
        elif any(word in message_lower for word in ['cena', 'cenar', 'noche']):
            preferences['horario_comida'] = ['cena']
        
        if any(word in message_lower for word in ['romÃ¡ntico', 'pareja', 'cita', 'Ã­ntimo']):
            preferences['ambiente'] = ['romantico']
        elif any(word in message_lower for word in ['familiar', 'familia', 'niÃ±os']):
            preferences['ambiente'] = ['familiar']
        elif any(word in message_lower for word in ['tranquilo', 'silencioso', 'relajado']):
            preferences['ambiente'] = ['tranquilo']
        
        if any(word in message_lower for word in ['cita', 'date', 'romÃ¡ntico']):
            preferences['ocasion'] = ['cita']
        elif any(word in message_lower for word in ['familia', 'familiar', 'niÃ±os']):
            preferences['ocasion'] = ['familia']
        elif any(word in message_lower for word in ['trabajo', 'negocios', 'reuniÃ³n']):
            preferences['ocasion'] = ['negocios']
        
        return preferences
    
    def generate_recommendation_text(self, establishments: List[Dict], user_query: str) -> str:
        if not establishments:
            return "No encontre establecimientos que coincidan exactamente con tus preferencias, pero te recomiendo explorar las opciones disponibles en el centro de Sucre donde hay gran variedad de restaurantes."
        
        if self.provider == "fallback":
            return self._generate_recommendation_fallback(establishments, user_query)
        
        establishments_info = []
        for est in establishments:
            info = f"- {est['name']} (Zona: {est['zone']}): {est['description']}"
            if est.get('establishment_types'):
                info += f" - Tipos: {', '.join(est['establishment_types'])}"
            if est.get('phone'):
                info += f" - Telefono: {est['phone']}"
            establishments_info.append(info)
        
        establishments_text = "\n".join(establishments_info)
        
        recommendation_prompt = f"Basandote en la consulta del usuario y el establecimiento disponible, genera una recomendacion personalizada y concisa. Consulta del usuario: {user_query}. Establecimiento recomendado: {establishments_text}. Instrucciones: 1. Recomienda unicamente este establecimiento de forma entusiasta 2. Explica en maximo 3 lineas por que es perfecto para lo que busca 3. Menciona 2-3 detalles relevantes (ubicacion, ambiente, especialidad) 4. Incluye informacion de contacto (zona y telefono) 5. Usa un tono amigable pero conciso 6. Termina con una pregunta breve para continuar la conversacion. Genera una recomendacion breve y atractiva:"

        return self.generate_response(recommendation_prompt, max_tokens=300)
    
    def _generate_recommendation_fallback(self, establishments: List[Dict], user_query: str) -> str:
        if establishments:
            est = establishments[0]
            return f"Te recomiendo **{est['name']}** en {est['zone']}. {est['description'][:100]}... Es perfecto para lo que buscas. Te gustaria mas informacion?"
        
        return "Encontre varias opciones interesantes para ti. Te gustaria que te de mas detalles sobre alguna en particular?"
    
    def check_connection(self) -> bool:
        if self.provider == "fallback":
            return True
            
        try:
            test_response = self.generate_response("test", max_tokens=10)
            return "error" not in test_response.lower()
        except:
            return False
