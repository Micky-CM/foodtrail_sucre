from django.shortcuts import render, get_object_or_404
from establishments.models import Establishment, EstablishmentType, MealType
from menu.models import MenuItemType, MenuItem

from urllib.parse import urlencode
from django.conf import settings

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