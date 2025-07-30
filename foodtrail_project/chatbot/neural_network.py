import numpy as np
import json
import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class NeuralNetworkClassifier:

    
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
        
        self.feature_patterns = {
            'tiempo_comida': {
                'desayuno': ['desayuno', 'maÃ±ana', 'morning'],
                'almuerzo': ['almuerzo', 'almorzar', 'mediodia', 'lunch'],
                'cena': ['cena', 'cenar', 'noche', 'dinner'],
                'merienda': ['merienda', 'snack', 'tarde']
            },
            'grupo_size': {
                'solo': ['solo', 'una persona', 'individual'],
                'pareja': ['dos personas', 'pareja', 'cita', 'dos'],
                'grupo_pequeÃ±o': ['tres', 'cuatro', 'pocos', 'grupo pequeÃ±o'],
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
                'futuro': ['maÃ±ana', 'proximo', 'siguiente', 'planear']
            }
        }
        
        self.build_vocabulary()
    
    def build_vocabulary(self):
        word_index = 0
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword not in self.vocabulary:
                    self.vocabulary[keyword] = word_index
                    word_index += 1
        
        for feature_type, feature_dict in self.feature_patterns.items():
            for feature, keywords in feature_dict.items():
                for keyword in keywords:
                    if keyword not in self.vocabulary:
                        self.vocabulary[keyword] = word_index
                        word_index += 1
        
        logger.info(f"Vocabulario construido con {len(self.vocabulary)} palabras")
    
    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        text = ' '.join(text.split())
        
        return text
    
    def text_to_vector(self, text: str) -> np.ndarray:
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        vector = np.zeros(len(self.vocabulary))
        
        for word in words:
            if word in self.vocabulary:
                vector[self.vocabulary[word]] += 1
        
        if np.sum(vector) > 0:
            vector = vector / np.sum(vector)
        
        return vector
    
    def classify_intent(self, text: str) -> Tuple[str, float]:

        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword in processed_text:
                    if keyword in words:
                        score += 2.0
                    else:
                        score += 1.0
            
            intent_scores[intent] = score / total_keywords if total_keywords > 0 else 0.0
        
        if not intent_scores or max(intent_scores.values()) == 0:
            return 'consulta_general', 0.5
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
        
        return best_intent, min(confidence, 1.0)
    
    def extract_features(self, text: str) -> Dict[str, List[str]]:

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
 
        intent, confidence = self.classify_intent(text)
        features = self.extract_features(text)
        
        entities = self._extract_entities(text)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'features': features,
            'entities': entities,
            'processed_text': self.preprocess_text(text)
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        processed_text = self.preprocess_text(text)
        entities = {}
        
        typical_dishes = [
            'pique macho', 'mondongo', 'salteÃ±a', 'empanada', 'api', 'buÃ±uelo',
            'chicharron', 'fricasÃ©', 'lechon', 'chorizo', 'morcilla', 'asado'
        ]
        
        found_dishes = []
        for dish in typical_dishes:
            if dish in processed_text:
                found_dishes.append(dish)
        
        if found_dishes:
            entities['platos_tipicos'] = found_dishes
        
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
        
        import re
        numbers = re.findall(r'\b(?:una|un|dos|tres|cuatro|cinco|seis|\d+)\b', processed_text)
        if numbers:
            entities['numeros'] = numbers
        
        return entities
    
    def get_response_template(self, intent: str) -> str:
        templates = {
            'buscar_restaurante': "Entiendo que buscas un lugar para comer. Â¿PodrÃ­as decirme quÃ© tipo de ambiente prefieres o para quÃ© ocasiÃ³n?",
            'buscar_comida_especifica': "Perfecto, me dices quÃ© tipo de comida especÃ­fica te interesa. DÃ©jame buscar los mejores lugares para eso.",
            'buscar_ambiente': "Excelente, veo que tienes preferencias especÃ­ficas sobre el ambiente. Te ayudo a encontrar el lugar perfecto.",
            'buscar_por_ocasion': "Entiendo que es para una ocasiÃ³n especial. Eso me ayuda mucho a recomendarte el lugar ideal.",
            'consulta_general': "Estoy aquÃ­ para ayudarte con informaciÃ³n sobre restaurantes en Sucre. Â¿QuÃ© te gustarÃ­a saber?",
            'saludo': "Â¡Hola! Soy FoodTrail AI, tu asistente para encontrar los mejores lugares gastronÃ³micos en Sucre. Â¿En quÃ© puedo ayudarte?",
            'agradecimiento': "Â¡De nada! Es un placer ayudarte. Â¿Hay algo mÃ¡s sobre restaurantes en Sucre que te gustarÃ­a saber?"
        }
        
        return templates.get(intent, "Entiendo. Â¿Puedes darme mÃ¡s detalles sobre lo que buscas?")
    
    def should_search_establishments(self, intent: str) -> bool:
        search_intents = [
            'buscar_restaurante',
            'buscar_comida_especifica', 
            'buscar_ambiente',
            'buscar_por_ocasion'
        ]
        return intent in search_intents
