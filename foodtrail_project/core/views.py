from django.shortcuts import render
from establishments.models import Establishment, EstablishmentType, MealType
from menu.models import MenuItemType

def home(request):
    # Obtener todos los tipos para los filtros
    establishment_types = EstablishmentType.objects.all()
    meal_types = MealType.objects.all()
    menu_item_types = MenuItemType.objects.all()
    
    # Obtener parámetros de filtro
    establishment_type_filter = request.GET.get('establishment_type')
    meal_type_filter = request.GET.get('meal_type')
    menu_item_type_filter = request.GET.get('menu_item_type')
    
    # Filtrar establecimientos
    establishments = Establishment.objects.all()
    
    if establishment_type_filter:
        establishments = establishments.filter(establishment_types__slug=establishment_type_filter)
    
    if meal_type_filter:
        establishments = establishments.filter(meal_types__slug=meal_type_filter)
    
    if menu_item_type_filter:
        establishments = establishments.filter(
            menu_items__menu_item_types__slug=menu_item_type_filter
        ).distinct()
    
    context = {
        'establishments': establishments,
        'establishment_types': establishment_types,
        'meal_types': meal_types,
        'menu_item_types': menu_item_types,
        'active_filters': {
            'establishment_type': establishment_type_filter,
            'meal_type': meal_type_filter,
            'menu_item_type': menu_item_type_filter,
        }
    }
    return render(request, 'core/home.html', context)