import requests
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    """Cliente para interactuar con Ollama API local"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 500) -> str:
        """
        Genera una respuesta usando Ollama
        
        Args:
            prompt: El prompt del usuario
            context: Contexto adicional para la conversación
            max_tokens: Número máximo de tokens en la respuesta
            
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            # Construir el prompt completo con contexto
            full_prompt = self._build_prompt(prompt, context)
            
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Lo siento, no pude generar una respuesta.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error conectando con Ollama: {e}")
            return "Lo siento, hay un problema con el servicio de IA. Por favor, intenta de nuevo más tarde."
        except Exception as e:
            logger.error(f"Error inesperado en OllamaClient: {e}")
            return "Ocurrió un error inesperado. Por favor, intenta de nuevo."
    
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

"""
        
        if context:
            full_prompt = f"{system_prompt}\n\nContexto de la conversación:\n{context}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
        else:
            full_prompt = f"{system_prompt}\n\nUsuario: {user_prompt}\n\nFoodTrail AI:"
            
        return full_prompt
    
    def extract_preferences(self, user_message: str) -> Dict[str, List[str]]:
        """
        Extrae preferencias del mensaje del usuario usando IA
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Dict con las preferencias extraídas
        """
        extraction_prompt = f"""
Analiza el siguiente mensaje de un usuario que busca recomendaciones de restaurantes y extrae la información en formato JSON.

Mensaje del usuario: "{user_message}"

Extrae la siguiente información y devuelve SOLO un JSON válido (sin texto adicional):

{{
    "tipo_establecimiento": ["restaurante", "cafeteria", "pub", "etc"],
    "tipo_comida": ["tradicional", "moderna", "italiana", "etc"],
    "horario_comida": ["desayuno", "almuerzo", "cena", "merienda"],
    "ambiente": ["romantico", "familiar", "tranquilo", "animado", "etc"],
    "ocasion": ["cita", "familia", "negocios", "celebracion", "etc"],
    "presupuesto": ["economico", "medio", "alto"],
    "caracteristicas": ["wifi", "parking", "terraza", "etc"]
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
                preferences = json.loads(json_str)
                return preferences
            else:
                logger.warning("No se pudo extraer JSON válido de la respuesta")
                return {}
                
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error extrayendo preferencias: {e}")
            return {}
    
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
            return "Lo siento, no encontré establecimientos que coincidan exactamente con tus preferencias. ¿Podrías darme más detalles sobre lo que buscas?"
        
        # Preparar información de establecimientos para el prompt
        establishments_info = []
        for est in establishments:
            info = f"""
Nombre: {est['name']}
Descripción: {est['description']}
Zona: {est['zone']}
Tipos: {', '.join(est['establishment_types'])}
Horarios: {', '.join(est['meal_types'])}
Teléfono: {est['phone']}
"""
            establishments_info.append(info)
        
        establishments_text = "\n---\n".join(establishments_info)
        
        recommendation_prompt = f"""
Basándote en la consulta del usuario y los establecimientos disponibles, genera una recomendación personalizada y atractiva.

Consulta del usuario: "{user_query}"

Establecimientos disponibles:
{establishments_text}

Instrucciones:
1. Recomienda máximo 2 establecimientos que mejor se adapten a la consulta
2. Explica específicamente por qué cada lugar es perfecto para lo que busca el usuario
3. Menciona detalles relevantes como ubicación, ambiente, especialidades
4. Usa un tono amigable y entusiasta
5. Incluye información práctica como zona y teléfono
6. Termina preguntando si necesita más información o tiene otras preferencias

Genera tu recomendación:
"""
        
        return self.generate_response(recommendation_prompt, max_tokens=600)
    
    def check_connection(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
