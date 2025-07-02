from django.core.management.base import BaseCommand
from establishments.models import EstablishmentType, MealType, Establishment, Image
from menu.models import MenuItemType, MenuItem


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de datos...'))
        
        # Crear tipos de establecimiento
        restaurant_type, created = EstablishmentType.objects.get_or_create(
            name='Restaurante',
            defaults={'description': 'Establecimiento de comida completa'}
        )
        
        cafeteria_type, created = EstablishmentType.objects.get_or_create(
            name='Cafetería',
            defaults={'description': 'Lugar para café y comida ligera'}
        )
        
        pub_type, created = EstablishmentType.objects.get_or_create(
            name='Pub',
            defaults={'description': 'Bar con ambiente relajado'}
        )
        
        # Crear tipos de comida
        breakfast_type, created = MealType.objects.get_or_create(name='Desayuno')
        lunch_type, created = MealType.objects.get_or_create(name='Almuerzo')
        dinner_type, created = MealType.objects.get_or_create(name='Cena')
        snack_type, created = MealType.objects.get_or_create(name='Merienda')
        
        # Crear tipos de menú
        main_course, created = MenuItemType.objects.get_or_create(name='Plato Principal')
        appetizer, created = MenuItemType.objects.get_or_create(name='Entrada')
        dessert, created = MenuItemType.objects.get_or_create(name='Postre')
        beverage, created = MenuItemType.objects.get_or_create(name='Bebida')
        
        # Crear establecimientos
        establishments_data = [
            {
                'name': 'Nativa',
                'description': 'Restaurante de comida tradicional boliviana con un ambiente acogedor y auténtico. Especializado en platos típicos de Sucre y Bolivia.',
                'phone': '+591 4 123-4567',
                'zone': 'Centro Histórico',
                'street': 'Calle Nicolás Ortiz',
                'number': '142',
                'types': [restaurant_type],
                'meals': [lunch_type, dinner_type],
                'images': ['nativa1.jpg', 'nativa2.jpg', 'nativa3.jpg']
            },
            {
                'name': 'La Posada',
                'description': 'Restaurante familiar con más de 30 años de tradición gastronómica. Ofrece una variedad de platos criollos y cocina internacional.',
                'phone': '+591 4 234-5678',
                'zone': 'Centro',
                'street': 'Plaza 25 de Mayo',
                'number': '45',
                'types': [restaurant_type],
                'meals': [breakfast_type, lunch_type, dinner_type],
                'images': ['posada1.jpg', 'posada2.jpg', 'posada3.jpg']
            },
            {
                'name': 'Solar Café',
                'description': 'Cafetería moderna con los mejores granos de café boliviano. Ambiente perfecto para trabajar y relajarse con vista al centro histórico.',
                'phone': '+591 4 345-6789',
                'zone': 'Centro Histórico',
                'street': 'Calle Audiencia',
                'number': '67',
                'types': [cafeteria_type],
                'meals': [breakfast_type, snack_type],
                'images': ['solar1.jpg', 'solar2.jpg', 'solar3.jpg']
            }
        ]
        
        for est_data in establishments_data:
            establishment, created = Establishment.objects.get_or_create(
                name=est_data['name'],
                defaults={
                    'description': est_data['description'],
                    'phone': est_data['phone'],
                    'zone': est_data['zone'],
                    'street': est_data['street'],
                    'number': est_data['number'],
                }
            )
            
            if created:
                # Agregar tipos de establecimiento
                establishment.establishment_types.set(est_data['types'])
                establishment.meal_types.set(est_data['meals'])
                
                # Crear imágenes
                for img_name in est_data['images']:
                    Image.objects.get_or_create(
                        establishment=establishment,
                        image=f'establishments/{img_name}',
                        defaults={'caption': f'Imagen de {establishment.name}'}
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Establecimiento "{establishment.name}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Establecimiento "{establishment.name}" ya existe')
                )
        
        # Crear algunos elementos de menú de ejemplo
        nativa = Establishment.objects.get(name='Nativa')
        posada = Establishment.objects.get(name='La Posada')
        solar = Establishment.objects.get(name='Solar Café')
        
        menu_items_data = [
            {
                'establishment': nativa,
                'name': 'Pique Macho',
                'description': 'Plato tradicional con carne, papas, huevos y ensalada',
                'price': 45.00,
                'types': [main_course],
                'image': 'nativa_comida1.jpg'
            },
            {
                'establishment': nativa,
                'name': 'Mondongo Chuquisaqueño',
                'description': 'Sopa tradicional de mote con carne de res',
                'price': 35.00,
                'types': [main_course],
                'image': 'nativa_comida2.jpg'
            },
            {
                'establishment': posada,
                'name': 'Asado de Cordero',
                'description': 'Cordero asado con papas y verduras al horno',
                'price': 65.00,
                'types': [main_course],
                'image': 'posada_comida1.jpg'
            },
            {
                'establishment': solar,
                'name': 'Café Boliviano Premium',
                'description': 'Café de grano especial de los Yungas de La Paz',
                'price': 18.00,
                'types': [beverage],
                'image': 'solar_comida1.jpg'
            }
        ]
        
        for item_data in menu_items_data:
            menu_item, created = MenuItem.objects.get_or_create(
                establishment=item_data['establishment'],
                name=item_data['name'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price'],
                    'image': f'menu_items/{item_data["image"]}'
                }
            )
            
            if created:
                menu_item.menu_item_types.set(item_data['types'])
                self.stdout.write(
                    self.style.SUCCESS(f'Item de menú "{menu_item.name}" creado')
                )
        
        self.stdout.write(
            self.style.SUCCESS('¡Población de datos completada exitosamente!')
        )
