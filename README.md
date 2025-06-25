# FoodTrail Sucre 🍽️

Una plataforma web para explorar la rica gastronomía de Sucre, Bolivia. Descubre los mejores restaurantes, cafés y bares de la ciudad, sus especialidades y menús.

## Características Principales 🌟

- 🏠 Página principal con lista de establecimientos
- 🔍 Filtros por tipo de establecimiento, tipo de comida y categorías de menú
- 📱 Diseño responsive que funciona en móviles, tablets y escritorio
- 🖼️ Galería de imágenes para cada establecimiento
- 🍽️ Visualización de menús y precios

## Requisitos Previos 🛠️

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

## Instalación Local 💻

1. **Clona el repositorio**:
   ```bash
   git clone [https://github.com/Micky-CM/foodtrail_sucre.git](https://github.com/Micky-CM/foodtrail_sucre.git)
   cd foodtrail_sucre

2. **Crea un entorno virtual (recomendado)**:
    En Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate

    En Linux/Mac:
   ```bash
   python -m venv venv
   source venv/bin/activate

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt

4. **Ejecuta las migraciones**:
   ```bash
   python manage.py migrate

5. **Crea un superusuario**:
   ```bash
   python manage.py createsuperuser

6. **Inicia el servidor de desarrollo**:
   ```bash
   python manage.py runserver

7. **Accede a la aplicación**:
   Abre tu navegador y ve a `http://localhost:8000` para ver la aplicación.

## Estructura del Proyecto 📁
```
foodtrail_sucre/
├── foodtrail_project/      # Configuración principal del proyecto
├── core/                   # Aplicación principal
├── establishments/         # Aplicación de establecimientos
├── menu/                   # Aplicación de menús
├── templates/              # Plantillas HTML
├── manage.py
└── requirements.txt

