from django.contrib import admin
from .models import EstablishmentType, MealType, Establishment, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ('image', 'caption')

class EstablishmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class MealTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'phone', 'get_establishment_types', 'get_meal_types')
    list_filter = ('establishment_types', 'meal_types', 'zone')
    search_fields = ('name', 'description', 'zone', 'street')
    filter_horizontal = ('establishment_types', 'meal_types')
    inlines = [ImageInline]
    
    def get_establishment_types(self, obj):
        return ", ".join([t.name for t in obj.establishment_types.all()])
    get_establishment_types.short_description = 'Tipos de Establecimiento'
    
    def get_meal_types(self, obj):
        return ", ".join([t.name for t in obj.meal_types.all()])
    get_meal_types.short_description = 'Horarios de Comida'

# Registrar los modelos con sus respectivas configuraciones
admin.site.register(EstablishmentType, EstablishmentTypeAdmin)
admin.site.register(MealType, MealTypeAdmin)
admin.site.register(Establishment, EstablishmentAdmin)
