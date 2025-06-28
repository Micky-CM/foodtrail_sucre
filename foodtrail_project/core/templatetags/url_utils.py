from django import template
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
from django.http import QueryDict

register = template.Library()

@register.simple_tag(takes_context=True)
def toggle_filter(context, param_name, param_value):
    """
    Alterna un filtro en la URL actual.
    Si el valor ya está en los parámetros, lo elimina; de lo contrario, lo añade.
    """
    request = context.get('request')
    if not request:
        return ''
        
    # Crear una copia mutable de los parámetros GET
    params = request.GET.copy()
    
    # Obtener los valores actuales del parámetro
    current_values = params.getlist(param_name)
    
    if param_value in current_values:
        # Si el valor ya está en los parámetros, lo eliminamos
        values = [v for v in current_values if v != param_value]
        if values:
            params.setlist(param_name, values)
        else:
            # Si no quedan valores, eliminamos el parámetro
            params.pop(param_name, None)
    else:
        # Si el valor no está, lo añadimos
        params.appendlist(param_name, param_value)
    
    # Reconstruir la URL
    return f"?{params.urlencode()}" if params else "?"
