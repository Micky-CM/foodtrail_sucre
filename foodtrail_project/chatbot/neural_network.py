import numpy as np
import json
import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class NeuralNetworkClassifier:
    """
    Red neuronal simple para clasificar intenciones y extraer características
    del texto de entrada del usuario
    """
    
    def __init__(self):
        self.vocabulary = {}
        self.intent_classes = [
            'buscar_restaurante',
            'buscar_comida_especifica', 
            'buscar_ambiente',
            'buscar_por_ocasion',
            'consulta_general',
            'saludo',
            'agradecimiento'
        ]
        
        # Palabras clave para cada intención (mejoradas)
        self.intent_keywords = {
            'buscar_restaurante': [
                'restaurante', 'lugar', 'sitio', 'donde', 'recomienda', 'recomendacion',
                'comer', 'comida', 'almorzar', 'cenar', 'desayunar', 'busco',
                'quiero', 'necesito', 'buen', 'buena', 'mejor', 'mejores'
            ],
            'buscar_comida_especifica': [
                'pique', 'mondongo', 'pasta', 'pizza', 'sopa', 'asado', 'pollo',
                'carne', 'pescado', 'vegetariano', 'plato', 'tradicional',
                'italiana', 'china', 'japonesa', 'mexicana', 'boliviana'
            ],
            'buscar_ambiente': [
                'romantico', 'tranquilo', 'familiar', 'animado', 'acogedor',
                'elegante', 'casual', 'moderno', 'tradicional', 'ambiente',
                'intimo', 'privado', 'silencioso', 'ruidoso'
            ],
            'buscar_por_ocasion': [
                'cita', 'fecha', 'aniversario', 'cumpleanos', 'celebracion',
                'reunion', 'negocios', 'familia', 'amigos', 'pareja',
                'personas', 'grupo', 'dos', 'tres', 'cuatro', 'cinco'
            ],
            'consulta_general': [
                'informacion', 'horarios', 'precio', 'telefono', 'direccion',
                'ubicacion', 'menu', 'carta', 'como', 'cual', 'que',
                'cuanto', 'cuando', 'abierto', 'cerrado'
            ],
            'saludo': [
                'hola', 'buenas', 'buenos', 'saludos', 'hey', 'hi',
                'buenas tardes', 'buenas noches', 'buen dia'
            ],
            'agradecimiento': [
                'gracias', 'muchas gracias', 'perfecto', 'excelente', 'bien'
            ]
        }
        
        # Características específicas para extraer
        self.feature_patterns = {
            'tiempo_comida': {
                'desayuno': ['desayuno', 'mañana', 'morning'],
                'almuerzo': ['almuerzo', 'almorzar', 'mediodia', 'lunch'],
                'cena': ['cena', 'cenar', 'noche', 'dinner'],
                'merienda': ['merienda', 'snack', 'tarde']
            },
            'grupo_size': {
                'solo': ['solo', 'una persona', 'individual'],
                'pareja': ['dos personas', 'pareja', 'cita', 'dos'],
                'grupo_pequeño': ['tres', 'cuatro', 'pocos', 'grupo pequeño'],
                'grupo_grande': ['muchos', 'grupo', 'familia grande', 'varios']
            },
            'presupuesto': {
                'economico': ['barato', 'economico', 'poco dinero', 'accesible'],
                'medio': ['normal', 'medio', 'regular', 'razonable'],
                'alto': ['caro', 'fino', 'gourmet', 'premium', 'lujo']
            },
            'urgencia': {
                'ahora': ['ahora', 'ya', 'inmediato', 'rapido'],
                'hoy': ['hoy', 'esta noche', 'este mediodia'],
                'futuro': ['mañana', 'proximo', 'siguiente', 'planear']
            }
        }
        
        self.build_vocabulary()
    
    def build_vocabulary(self):
        """Construye el vocabulario basado en las palabras clave"""
        word_index = 0
        
        # Agregar palabras de intenciones
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword not in self.vocabulary:
                    self.vocabulary[keyword] = word_index
                    word_index += 1
        
        # Agregar palabras de características
        for feature_type, feature_dict in self.feature_patterns.items():
            for feature, keywords in feature_dict.items():
                for keyword in keywords:
                    if keyword not in self.vocabulary:
                        self.vocabulary[keyword] = word_index
                        word_index += 1
        
        logger.info(f"Vocabulario construido con {len(self.vocabulary)} palabras")
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto de entrada"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalizar espacios
        text = ' '.join(text.split())
        
        return text
    
    def text_to_vector(self, text: str) -> np.ndarray:
        """Convierte texto a vector numérico basado en el vocabulario"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        # Vector con el tamaño del vocabulario
        vector = np.zeros(len(self.vocabulary))
        
        # Contar ocurrencias de palabras
        for word in words:
            if word in self.vocabulary:
                vector[self.vocabulary[word]] += 1
        
        # Normalizar el vector
        if np.sum(vector) > 0:
            vector = vector / np.sum(vector)
        
        return vector
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Clasifica la intención del texto
        
        Args:
            text: Texto a clasificar
            
        Returns:
            Tuple con (intención_predicha, confianza)
        """
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        intent_scores = {}
        
        # Calcular puntuación para cada intención
        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword in processed_text:
                    # Puntuación más alta para coincidencias exactas de palabras
                    if keyword in words:
                        score += 2.0
                    else:
                        score += 1.0
            
            # Normalizar puntuación
            intent_scores[intent] = score / total_keywords if total_keywords > 0 else 0.0
        
        # Encontrar la intención con mayor puntuación
        if not intent_scores or max(intent_scores.values()) == 0:
            return 'consulta_general', 0.5
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
        
        return best_intent, min(confidence, 1.0)
    
    def extract_features(self, text: str) -> Dict[str, List[str]]:
        """
        Extrae características específicas del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con características extraídas
        """
        processed_text = self.preprocess_text(text)
        features = {}
        
        for feature_type, feature_patterns in self.feature_patterns.items():
            detected_features = []
            
            for feature_name, keywords in feature_patterns.items():
                for keyword in keywords:
                    if keyword in processed_text:
                        if feature_name not in detected_features:
                            detected_features.append(feature_name)
                        break
            
            if detected_features:
                features[feature_type] = detected_features
        
        return features
    
    def analyze_message(self, text: str) -> Dict[str, any]:
        """
        Análisis completo del mensaje del usuario
        
        Args:
            text: Mensaje del usuario
            
        Returns:
            Diccionario con análisis completo
        """
        intent, confidence = self.classify_intent(text)
        features = self.extract_features(text)
        
        # Extraer entidades específicas
        entities = self._extract_entities(text)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'features': features,
            'entities': entities,
            'processed_text': self.preprocess_text(text)
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrae entidades específicas como nombres de platos, lugares, etc."""
        processed_text = self.preprocess_text(text)
        entities = {}
        
        # Platos típicos bolivianos/chuquisaqueños
        typical_dishes = [
            'pique macho', 'mondongo', 'salteña', 'empanada', 'api', 'buñuelo',
            'chicharron', 'fricasé', 'lechon', 'chorizo', 'morcilla', 'asado'
        ]
        
        found_dishes = []
        for dish in typical_dishes:
            if dish in processed_text:
                found_dishes.append(dish)
        
        if found_dishes:
            entities['platos_tipicos'] = found_dishes
        
        # Zonas de Sucre
        zones = [
            'centro historico', 'centro', 'bolivar', 'recoleta', 'san sebastian',
            'san roque', 'san lazaro', 'villa cristal'
        ]
        
        found_zones = []
        for zone in zones:
            if zone in processed_text:
                found_zones.append(zone)
        
        if found_zones:
            entities['zonas'] = found_zones
        
        # Números (para cantidad de personas)
        import re
        numbers = re.findall(r'\b(?:una|un|dos|tres|cuatro|cinco|seis|\d+)\b', processed_text)
        if numbers:
            entities['numeros'] = numbers
        
        return entities
    
    def get_response_template(self, intent: str) -> str:
        """Retorna un template de respuesta basado en la intención"""
        templates = {
            'buscar_restaurante': "Entiendo que buscas un lugar para comer. ¿Podrías decirme qué tipo de ambiente prefieres o para qué ocasión?",
            'buscar_comida_especifica': "Perfecto, me dices qué tipo de comida específica te interesa. Déjame buscar los mejores lugares para eso.",
            'buscar_ambiente': "Excelente, veo que tienes preferencias específicas sobre el ambiente. Te ayudo a encontrar el lugar perfecto.",
            'buscar_por_ocasion': "Entiendo que es para una ocasión especial. Eso me ayuda mucho a recomendarte el lugar ideal.",
            'consulta_general': "Estoy aquí para ayudarte con información sobre restaurantes en Sucre. ¿Qué te gustaría saber?",
            'saludo': "¡Hola! Soy FoodTrail AI, tu asistente para encontrar los mejores lugares gastronómicos en Sucre. ¿En qué puedo ayudarte?",
            'agradecimiento': "¡De nada! Es un placer ayudarte. ¿Hay algo más sobre restaurantes en Sucre que te gustaría saber?"
        }
        
        return templates.get(intent, "Entiendo. ¿Puedes darme más detalles sobre lo que buscas?")
    
    def should_search_establishments(self, intent: str) -> bool:
        """Determina si se debe buscar establecimientos basado en la intención"""
        search_intents = [
            'buscar_restaurante',
            'buscar_comida_especifica', 
            'buscar_ambiente',
            'buscar_por_ocasion'
        ]
        return intent in search_intents
