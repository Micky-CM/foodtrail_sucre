from django.db.models import Q
from establishments.models import Establishment, EstablishmentType, MealType
from menu.models import MenuItem
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Motor de recomendaciones basado en preferencias del usuario"""
    
    def __init__(self):
        self.establishment_weights = {
            'exact_match': 3.0,
            'partial_match': 1.5,
            'related_match': 1.0,
            'default': 0.5
        }
    
    def find_establishments(self, preferences: Dict[str, List[str]], user_query: str = "") -> List[Dict[str, Any]]:
        """
        Encuentra establecimientos basándose en las preferencias extraídas
        
        Args:
            preferences: Diccionario con preferencias del usuario
            user_query: Consulta original del usuario para contexto
            
        Returns:
            Lista de establecimientos ordenados por relevancia
        """
        try:
            # Obtener todos los establecimientos
            establishments = Establishment.objects.prefetch_related(
                'establishment_types',
                'meal_types',
                'images',
                'menu_items'
            ).all()
            
            scored_establishments = []
            
            for establishment in establishments:
                score = self._calculate_establishment_score(establishment, preferences, user_query)
                
                if score > 0:  # Solo incluir establecimientos con alguna puntuación
                    establishment_data = self._format_establishment_data(establishment)
                    establishment_data['relevance_score'] = score
                    scored_establishments.append(establishment_data)
            
            # Ordenar por puntuación de relevancia
            scored_establishments.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Retornar solo la mejor recomendación
            return scored_establishments[:1]
            
        except Exception as e:
            logger.error(f"Error en find_establishments: {e}")
            return []
    
    def _calculate_establishment_score(self, establishment: Establishment, preferences: Dict[str, List[str]], user_query: str) -> float:
        """Calcula la puntuación de un establecimiento basado en las preferencias"""
        score = 0.0
        
        # Puntuación base para todos los establecimientos
        score += self.establishment_weights['default']
        
        # Evaluar tipo de establecimiento
        est_types = [et.name.lower() for et in establishment.establishment_types.all()]
        tipo_establecimiento = preferences.get('tipo_establecimiento', [])
        
        # Asegurar que sea una lista
        if not isinstance(tipo_establecimiento, list):
            tipo_establecimiento = [tipo_establecimiento] if tipo_establecimiento else []
            
        for tipo in tipo_establecimiento:
            if any(tipo.lower() in et for et in est_types):
                score += self.establishment_weights['exact_match']
        
        # Evaluar horarios de comida
        meal_types = [mt.name.lower() for mt in establishment.meal_types.all()]
        horario_comida = preferences.get('horario_comida', [])
        
        # Asegurar que sea una lista
        if not isinstance(horario_comida, list):
            horario_comida = [horario_comida] if horario_comida else []
            
        for horario in horario_comida:
            if any(horario.lower() in mt for mt in meal_types):
                score += self.establishment_weights['exact_match']
        
        # Evaluar ambiente/ocasión por descripción
        ambiente_list = preferences.get('ambiente', [])
        ocasion_list = preferences.get('ocasion', [])
        
        # Manejar casos donde ambiente puede ser dict o list
        if isinstance(ambiente_list, dict):
            # Extraer valores True del diccionario
            ambiente_list = [k for k, v in ambiente_list.items() if v]
        if isinstance(ocasion_list, dict):
            ocasion_list = [k for k, v in ocasion_list.items() if v]
        
        # Asegurar que sean listas
        if not isinstance(ambiente_list, list):
            ambiente_list = [ambiente_list] if ambiente_list else []
        if not isinstance(ocasion_list, list):
            ocasion_list = [ocasion_list] if ocasion_list else []
            
        ambiente = ambiente_list + ocasion_list
        description = establishment.description.lower()
        
        for amb in ambiente:
            if self._check_ambience_match(amb.lower(), description):
                score += self.establishment_weights['partial_match']
        
        # Evaluar tipo de comida por descripción y menú
        tipo_comida = preferences.get('tipo_comida', [])
        
        # Asegurar que sea una lista
        if not isinstance(tipo_comida, list):
            tipo_comida = [tipo_comida] if tipo_comida else []
            
        for tipo in tipo_comida:
            if self._check_cuisine_match(tipo.lower(), establishment):
                score += self.establishment_weights['partial_match']
        
        # Puntuación adicional por palabras clave en la consulta original
        if user_query:
            score += self._check_query_keywords(user_query.lower(), establishment)
        
        return score
    
    def _check_ambience_match(self, ambience: str, description: str) -> bool:
        """Verifica si el ambiente coincide con la descripción"""
        ambience_keywords = {
            'romantico': ['romántico', 'íntimo', 'acogedor', 'especial', 'elegante'],
            'familiar': ['familiar', 'familia', 'niños', 'amplio', 'cómodo'],
            'tranquilo': ['tranquilo', 'relajado', 'pacífico', 'silencioso'],
            'animado': ['animado', 'vibrante', 'activo', 'lively'],
            'moderno': ['moderno', 'contemporáneo', 'actual'],
            'tradicional': ['tradicional', 'auténtico', 'típico', 'histórico'],
            'casual': ['casual', 'informal', 'relajado'],
            'elegante': ['elegante', 'fino', 'sofisticado', 'formal']
        }
        
        keywords = ambience_keywords.get(ambience, [ambience])
        return any(keyword in description for keyword in keywords)
    
    def _check_cuisine_match(self, cuisine_type: str, establishment: Establishment) -> bool:
        """Verifica si el tipo de comida coincide"""
        description = establishment.description.lower()
        
        cuisine_keywords = {
            'tradicional': ['tradicional', 'típico', 'boliviana', 'chuquisaqueña', 'autóctona'],
            'moderna': ['moderna', 'contemporánea', 'fusion', 'internacional'],
            'italiana': ['italiana', 'pasta', 'pizza'],
            'mexicana': ['mexicana', 'tacos', 'burritos'],
            'china': ['china', 'chino', 'oriental'],
            'vegetariana': ['vegetariana', 'vegana', 'saludable'],
            'rapida': ['rápida', 'fast', 'comida rápida'],
            'gourmet': ['gourmet', 'premium', 'especialidad']
        }
        
        keywords = cuisine_keywords.get(cuisine_type, [cuisine_type])
        
        # Verificar en descripción
        if any(keyword in description for keyword in keywords):
            return True
        
        # Verificar en elementos del menú si existe
        menu_items = establishment.menu_items.all()
        for item in menu_items:
            item_desc = f"{item.name} {item.description}".lower()
            if any(keyword in item_desc for keyword in keywords):
                return True
        
        return False
    
    def _check_query_keywords(self, query: str, establishment: Establishment) -> float:
        """Verifica palabras clave específicas de la consulta"""
        score = 0.0
        description = establishment.description.lower()
        name = establishment.name.lower()
        
        # Palabras clave especiales
        if 'noche' in query or 'nocturno' in query:
            if 'cena' in [mt.name.lower() for mt in establishment.meal_types.all()]:
                score += 1.0
        
        if 'dos personas' in query or 'pareja' in query or 'cita' in query:
            if any(word in description for word in ['íntimo', 'romántico', 'acogedor']):
                score += 1.0
        
        if 'grupo' in query or 'familia' in query or 'varios' in query:
            if any(word in description for word in ['amplio', 'familiar', 'grande']):
                score += 1.0
        
        # Verificar si el nombre del establecimiento está en la consulta
        if name in query or any(word in query for word in name.split()):
            score += 2.0
        
        return score
    
    def _format_establishment_data(self, establishment: Establishment) -> Dict[str, Any]:
        """Formatea los datos del establecimiento para la respuesta"""
        
        # Obtener imágenes
        images = []
        for img in establishment.images.all():
            images.append({
                'url': img.image.url if img.image else '',
                'caption': img.caption
            })
        
        # Obtener elementos del menú destacados
        featured_menu_items = []
        menu_items = establishment.menu_items.all()[:3]  # Top 3 items
        
        for item in menu_items:
            featured_menu_items.append({
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'types': [t.name for t in item.menu_item_types.all()]
            })
        
        return {
            'id': establishment.id,
            'name': establishment.name,
            'description': establishment.description,
            'phone': establishment.phone,
            'zone': establishment.zone,
            'street': establishment.street,
            'number': establishment.number,
            'establishment_types': [et.name for et in establishment.establishment_types.all()],
            'meal_types': [mt.name for mt in establishment.meal_types.all()],
            'images': images,
            'featured_menu_items': featured_menu_items,
            'latitude': float(establishment.latitude) if establishment.latitude else None,
            'longitude': float(establishment.longitude) if establishment.longitude else None,
        }
    
    def get_similar_establishments(self, establishment_id: int, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Encuentra establecimientos similares basados en tipos y características
        
        Args:
            establishment_id: ID del establecimiento de referencia
            limit: Número máximo de establecimientos similares a retornar
            
        Returns:
            Lista de establecimientos similares
        """
        try:
            reference = Establishment.objects.get(id=establishment_id)
            reference_types = reference.establishment_types.all()
            reference_meals = reference.meal_types.all()
            
            # Buscar establecimientos con tipos similares
            similar = Establishment.objects.filter(
                establishment_types__in=reference_types
            ).exclude(id=establishment_id).distinct()
            
            # También considerar horarios de comida similares
            meal_similar = Establishment.objects.filter(
                meal_types__in=reference_meals
            ).exclude(id=establishment_id).distinct()
            
            # Combinar y eliminar duplicados
            combined = (similar | meal_similar).distinct()[:limit]
            
            return [self._format_establishment_data(est) for est in combined]
            
        except Establishment.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"Error obteniendo establecimientos similares: {e}")
            return []
