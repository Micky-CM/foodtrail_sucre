from django.shortcuts import render, get_object_or_404
from establishments.models import Establishment, EstablishmentType, MealType
from menu.models import MenuItemType, MenuItem
from django.db.models import Q

from urllib.parse import urlencode
from django.conf import settings
import random

def home(request):
    # Obtener todos los tipos para los filtros
    establishment_types = EstablishmentType.objects.all()
    meal_types = MealType.objects.all()
    menu_item_types = MenuItemType.objects.all()
    
    # Obtener parámetros de filtro actuales (pueden ser múltiples por tipo)
    current_params = request.GET.copy()
    establishment_type_filters = request.GET.getlist('establishment_type')
    meal_type_filters = request.GET.getlist('meal_type')
    menu_item_type_filters = request.GET.getlist('menu_item_type')
    
    # Filtrar establecimientos
    establishments = Establishment.objects.all()
    
    # Aplicar filtros de tipo de establecimiento (OR dentro del mismo tipo, AND entre tipos)
    if establishment_type_filters:
        from django.db.models import Q
        establishment_query = Q()
        for et in establishment_type_filters:
            establishment_query |= Q(establishment_types__slug=et)
        establishments = establishments.filter(establishment_query).distinct()
    
    # Aplicar filtros de tipo de comida (OR dentro del mismo tipo, AND entre tipos)
    if meal_type_filters:
        from django.db.models import Q
        meal_query = Q()
        for mt in meal_type_filters:
            meal_query |= Q(meal_types__slug=mt)
        establishments = establishments.filter(meal_query).distinct()
    
    # Aplicar filtros de tipo de menú (OR dentro del mismo tipo, AND entre tipos)
    if menu_item_type_filters:
        from django.db.models import Q
        menu_item_query = Q()
        for mit in menu_item_type_filters:
            menu_item_query |= Q(menu_items__menu_item_types__slug=mit)
        establishments = establishments.filter(menu_item_query).distinct()
    
    # Función para construir URLs con múltiples parámetros
    def build_url(params_to_update):
        params = current_params.copy()
        for key, value in params_to_update.items():
            if value is None:
                params.pop(key, None)
            else:
                # Si el valor es una lista, la añadimos como lista
                if isinstance(value, list):
                    params.setlist(key, value)
                else:
                    params[key] = value
        return f"?{urlencode(params, doseq=True)}" if params else "?"
    
    # Obtener los nombres de los filtros activos
    active_filters_with_names = {}
    
    # Para tipos de establecimiento
    if establishment_type_filters:
        active_filters_with_names['establishment_type'] = {
            'name': 'Tipo de Establecimiento',
            'values': [{
                'slug': et,
                'name': next((t.name for t in establishment_types if t.slug == et), et)
            } for et in establishment_type_filters]
        }
    
    # Para tipos de comida
    if meal_type_filters:
        active_filters_with_names['meal_type'] = {
            'name': 'Tipo de Comida',
            'values': [{
                'slug': mt,
                'name': next((t.name for t in meal_types if t.slug == mt), mt)
            } for mt in meal_type_filters]
        }
    
    # Para tipos de plato
    if menu_item_type_filters:
        active_filters_with_names['menu_item_type'] = {
            'name': 'Tipo de Plato',
            'values': [{
                'slug': mit,
                'name': next((t.name for t in menu_item_types if t.slug == mit), mit)
            } for mit in menu_item_type_filters]
        }
    
    context = {
        'establishments': establishments,
        'establishment_types': establishment_types,
        'meal_types': meal_types,
        'menu_item_types': menu_item_types,
        'active_filters': active_filters_with_names,
        'build_url': build_url,
        'MEDIA_URL': settings.MEDIA_URL,
        'request': request
    }
    return render(request, 'core/home.html', context)

def establishment_detail(request, establishment_id):
    # Obtener el establecimiento o devolver 404 si no existe
    establishment = get_object_or_404(Establishment.objects.prefetch_related('images', 'establishment_types', 'meal_types'), 
                                     id=establishment_id)
    
    # Obtener los ítems del menú del establecimiento
    menu_items = MenuItem.objects.filter(establishment=establishment).select_related('establishment')
    
    context = {
        'establishment': establishment,
        'menu_items': menu_items,
    }
    return render(request, 'core/establishment_detail.html', context)

def landing_page(request):
    """Vista para la página principal con carrusel de establecimientos"""
    # Obtener establecimientos con imágenes para el carrusel
    establishments_with_images = Establishment.objects.filter(images__isnull=False).distinct()
    
    # Seleccionar máximo 5 establecimientos para el carrusel
    carousel_establishments = list(establishments_with_images[:5])
    
    # Si no hay suficientes, tomar algunos al azar
    if len(carousel_establishments) < 5:
        all_establishments = list(Establishment.objects.all())
        remaining = [est for est in all_establishments if est not in carousel_establishments]
        random.shuffle(remaining)
        carousel_establishments.extend(remaining[:5-len(carousel_establishments)])
    
    # Preparar datos para el carrusel con primera imagen de cada establecimiento
    carousel_data = []
    for establishment in carousel_establishments:
        first_image = establishment.images.first()
        carousel_data.append({
            'establishment': establishment,
            'image': first_image.image.url if first_image else '/static/images/default-restaurant.jpg',
            'name': establishment.name,
            'description': establishment.description[:100] + '...' if len(establishment.description) > 100 else establishment.description,
            'zone': establishment.zone,
        })
    
    context = {
        'carousel_establishments': carousel_data,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'core/landing_page.html', context)