from django.contrib import admin
from .models import MenuItemType, MenuItem

class MenuItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'establishment', 'price', 'get_menu_item_types')
    list_filter = ('establishment', 'menu_item_types')
    search_fields = ('name', 'description', 'establishment__name')
    filter_horizontal = ('menu_item_types',)
    list_select_related = ('establishment',)
    
    def get_menu_item_types(self, obj):
        return ", ".join([t.name for t in obj.menu_item_types.all()])
    get_menu_item_types.short_description = 'Tipos de Plato'

# Registrar los modelos
admin.site.register(MenuItemType, MenuItemTypeAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
