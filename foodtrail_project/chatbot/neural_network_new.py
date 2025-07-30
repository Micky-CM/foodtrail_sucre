import numpy as np
import json
import pickle
import os
from typing import List, Dict, Tuple, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re

logger = logging.getLogger(__name__)

class AdvancedNeuralChatbot:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or 'chatbot_model.pkl'
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=1000,
            stop_words=None,
            lowercase=True
        )
        self.classifier = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        
        self.intent_labels = [
            'buscar_restaurante',
            'buscar_comida_especifica', 
            'buscar_ambiente',
            'buscar_por_ocasion',
            'consulta_horarios',
            'consulta_precios',
            'consulta_ubicacion',
            'saludo',
            'agradecimiento',
            'despedida'
        ]
        
        self.entities_patterns = {
            'comida_boliviana': [
                'pique macho', 'mondongo', 'salteña', 'empanada', 'api con pastel',
                'buñuelo', 'chicharron', 'fricasé', 'lechon', 'chorizo chuquisaqueño',
                'morcilla', 'asado', 'llajua', 'locro', 'chairo', 'sopa de maní'
            ],
            'tipos_carne': [
                'pollo', 'res', 'cerdo', 'cordero', 'llama', 'pescado', 'mariscos',
                'vegetariano', 'vegano'
            ],
            'ambientes': [
                'romantico', 'familiar', 'tranquilo', 'animado', 'acogedor',
                'elegante', 'casual', 'moderno', 'tradicional', 'rustico',
                'intimo', 'espacioso', 'con musica', 'silencioso'
            ],
            'ocasiones': [
                'cita', 'aniversario', 'cumpleanos', 'reunion de trabajo',
                'almuerzo familiar', 'cena romantica', 'celebracion',
                'despedida de soltero', 'primera cita', 'reunion amigos'
            ],
            'horarios': [
                'desayuno', 'almuerzo', 'cena', 'merienda', 'brunch',
                'media mañana', 'media tarde', 'madrugada'
            ],
            'presupuesto': [
                'barato', 'economico', 'accesible', 'medio', 'normal',
                'caro', 'premium', 'gourmet', 'lujo'
            ],
            'ubicaciones_sucre': [
                'centro historico', 'plaza 25 de mayo', 'recoleta',
                'san sebastian', 'bolivar', 'san roque', 'san lazaro'
            ]
        }
        
        self.is_trained = False
        self.load_or_create_model()
    
    def generate_training_data(self) -> Tuple[List[str], List[str]]:
        training_texts = []
        training_labels = []
        
        restaurant_phrases = [
            "busco un restaurante", "donde puedo comer", "recomienda un lugar",
            "quiero ir a comer", "necesito un lugar para almorzar",
            "buscamos donde cenar", "que restaurante me recomiendas",
            "donde hay buena comida", "lugar para comer rico"
        ]
        for phrase in restaurant_phrases:
            training_texts.append(phrase)
            training_labels.append('buscar_restaurante')
        
        food_phrases = [
            "quiero comer pique macho", "donde venden salteñas",
            "busco comida tradicional", "quiero probar mondongo",
            "donde hacen buen asado", "comida boliviana autentica",
            "platos típicos chuquisaqueños", "quiero pasta italiana"
        ]
        for phrase in food_phrases:
            training_texts.append(phrase)
            training_labels.append('buscar_comida_especifica')
        
        ambience_phrases = [
            "lugar romantico para dos", "restaurante familiar",
            "ambiente tranquilo", "lugar acogedor", "sitio elegante",
            "ambiente casual", "lugar con buena musica", "restaurante intimo"
        ]
        for phrase in ambience_phrases:
            training_texts.append(phrase)
            training_labels.append('buscar_ambiente')
        
        occasion_phrases = [
            "para una cita", "celebrar aniversario", "cumpleanos",
            "reunion de trabajo", "almuerzo de negocios", "cena romantica",
            "celebracion familiar", "primera cita", "despedida"
        ]
        for phrase in occasion_phrases:
            training_texts.append(phrase)
            training_labels.append('buscar_por_ocasion')
        
        hours_phrases = [
            "horarios de atencion", "que hora abren", "hasta que hora",
            "horario de almuerzo", "atienden en la noche", "abierto domingos"
        ]
        for phrase in hours_phrases:
            training_texts.append(phrase)
            training_labels.append('consulta_horarios')
        
        price_phrases = [
            "precios del menu", "cuanto cuesta", "es caro", "economico",
            "rango de precios", "precio promedio", "menu del dia precio"
        ]
        for phrase in price_phrases:
            training_texts.append(phrase)
            training_labels.append('consulta_precios')
        
        location_phrases = [
            "donde queda", "direccion", "como llegar", "ubicacion",
            "en que zona esta", "cerca del centro", "direccion exacta"
        ]
        for phrase in location_phrases:
            training_texts.append(phrase)
            training_labels.append('consulta_ubicacion')
        
        greeting_phrases = [
            "hola", "buenos dias", "buenas tardes", "buenas noches",
            "saludos", "hey", "que tal", "como estas"
        ]
        for phrase in greeting_phrases:
            training_texts.append(phrase)
            training_labels.append('saludo')
        
        thanks_phrases = [
            "gracias", "muchas gracias", "perfecto", "excelente",
            "muy bien", "genial", "buenisimo", "exacto"
        ]
        for phrase in thanks_phrases:
            training_texts.append(phrase)
            training_labels.append('agradecimiento')
        
        goodbye_phrases = [
            "chau", "hasta luego", "nos vemos", "adios",
            "hasta la vista", "que tengas buen dia", "gracias por todo"
        ]
        for phrase in goodbye_phrases:
            training_texts.append(phrase)
            training_labels.append('despedida')
        
        return training_texts, training_labels
    
    def train_model(self):
        logger.info("Generando datos de entrenamiento...")
        texts, labels = self.generate_training_data()
        
        logger.info(f"Entrenando con {len(texts)} ejemplos...")
        
        X = self.vectorizer.fit_transform(texts)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        self.classifier.fit(X_train, y_train)
        
        y_pred = self.classifier.predict(X_test)
        logger.info("Reporte de clasificación:")
        logger.info(classification_report(y_test, y_pred))
        
        self.is_trained = True
        self.save_model()
    
    def save_model(self):
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'intent_labels': self.intent_labels,
                'is_trained': self.is_trained
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Modelo guardado en {self.model_path}")
        except Exception as e:
            logger.error(f"Error guardando modelo: {e}")
    
    def load_or_create_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.intent_labels = model_data['intent_labels']
                self.is_trained = model_data['is_trained']
                
                logger.info("Modelo cargado exitosamente")
            except Exception as e:
                logger.error(f"Error cargando modelo: {e}")
                self.train_model()
        else:
            logger.info("No se encontró modelo existente, entrenando nuevo modelo...")
            self.train_model()
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        if not self.is_trained:
            return 'buscar_restaurante', 0.5
        
        try:
            text_vector = self.vectorizer.transform([text])
            
            intent = self.classifier.predict(text_vector)[0]
            probabilities = self.classifier.predict_proba(text_vector)[0]
            confidence = max(probabilities)
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"Error en clasificación: {e}")
            return 'buscar_restaurante', 0.5
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        text_lower = text.lower()
        entities = {}
        
        for entity_type, patterns in self.entities_patterns.items():
            found_entities = []
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    found_entities.append(pattern)
            
            if found_entities:
                entities[entity_type] = found_entities
        
        numbers = re.findall(r'\b(?:una|un|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|\d+)\b', text_lower)
        if numbers:
            entities['cantidad_personas'] = numbers
        
        time_indicators = re.findall(r'\b(?:hoy|mañana|esta noche|este mediodia|ahora|ya|pronto)\b', text_lower)
        if time_indicators:
            entities['tiempo'] = time_indicators
        
        return entities
    
    def analyze_message(self, text: str) -> Dict[str, any]:
        intent, confidence = self.classify_intent(text)
        
        entities = self.extract_entities(text)
        
        sentiment = self._analyze_sentiment(text)
        
        preferences = self._extract_preferences(text, entities)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'sentiment': sentiment,
            'preferences': preferences,
            'processed_text': text.lower().strip()
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        positive_words = ['bueno', 'excelente', 'genial', 'perfecto', 'rico', 'delicioso']
        negative_words = ['malo', 'terrible', 'horrible', 'feo', 'caro', 'sucio']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positivo'
        elif negative_count > positive_count:
            return 'negativo'
        else:
            return 'neutral'
    
    def _extract_preferences(self, text: str, entities: Dict) -> Dict[str, List[str]]:
        preferences = {}
        
        if 'comida_boliviana' in entities:
            preferences['tipo_comida'] = ['tradicional', 'boliviana']
        
        if 'tipos_carne' in entities:
            preferences['tipo_carne'] = entities['tipos_carne']
        
        if 'ambientes' in entities:
            preferences['ambiente'] = entities['ambientes']
        
        if 'ocasiones' in entities:
            preferences['ocasion'] = entities['ocasiones']
        
        if 'horarios' in entities:
            preferences['horario_comida'] = entities['horarios']
        
        if 'presupuesto' in entities:
            preferences['presupuesto'] = entities['presupuesto']
        
        if 'ubicaciones_sucre' in entities:
            preferences['zona'] = entities['ubicaciones_sucre']
        
        return preferences
    
    def should_search_establishments(self, intent: str, confidence: float) -> bool:
        search_intents = [
            'buscar_restaurante',
            'buscar_comida_especifica',
            'buscar_ambiente',
            'buscar_por_ocasion'
        ]
        
        return intent in search_intents and confidence > 0.6
    
    def get_response_template(self, intent: str, entities: Dict = None) -> str:
        templates = {
            'buscar_restaurante': [
                "Perfecto, te ayudo a encontrar un lugar ideal. ",
                "Excelente, busquemos el restaurante perfecto para ti. ",
                "¡Genial! Vamos a encontrar el lugar ideal. "
            ],
            'buscar_comida_especifica': [
                "Entiendo que buscas algo específico, déjame encontrar los mejores lugares. ",
                "Perfecto, conozco lugares excelentes para eso. ",
                "¡Excelente elección! Te muestro las mejores opciones. "
            ],
            'buscar_ambiente': [
                "Me encanta que tengas claro el ambiente que buscas. ",
                "Perfecto, el ambiente es muy importante. ",
                "Excelente, vamos a encontrar el lugar con el ambiente ideal. "
            ],
            'buscar_por_ocasion': [
                "¡Qué emocionante! Te ayudo a encontrar el lugar perfecto para la ocasión. ",
                "Entiendo la importancia de la ocasión, busquemos algo especial. ",
                "Perfecto, cada ocasión merece el lugar ideal. "
            ],
            'saludo': [
                "¡Hola! Soy FoodTrail AI, tu guía gastronómica en Sucre. ",
                "¡Saludos! Estoy aquí para ayudarte a descubrir los mejores sabores de Sucre. ",
                "¡Bienvenido! Soy tu asistente especializado en gastronomía chuquisaqueña. "
            ]
        }
        
        template_list = templates.get(intent, ["Entiendo, ¿puedes darme más detalles? "])
        return np.random.choice(template_list)

def get_neural_classifier():
    return AdvancedNeuralChatbot()