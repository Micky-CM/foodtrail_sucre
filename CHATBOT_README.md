# 🤖 FoodTrail AI Chatbot

## Descripción

FoodTrail AI es un chatbot inteligente con red neuronal integrada que utiliza la API de Ollama (LLM local) para recomendar los mejores restaurantes y lugares gastronómicos en Sucre, Bolivia. El sistema combina procesamiento de lenguaje natural, clasificación de intenciones con redes neuronales y un motor de recomendaciones personalizado.

## 🚀 Características

### Red Neuronal Integrada
- **Clasificador de intenciones**: Analiza el mensaje del usuario para determinar qué tipo de consulta está haciendo
- **Extracción de entidades**: Identifica información específica como tipo de comida, ambiente, ocasión, presupuesto, etc.
- **Análisis de sentimiento**: Comprende el tono y las preferencias del usuario

### Motor de Recomendaciones
- **Búsqueda inteligente**: Encuentra establecimientos basándose en múltiples criterios
- **Puntuación de relevancia**: Clasifica recomendaciones por compatibilidad con las preferencias
- **Contexto conversacional**: Mantiene el historial para mejores recomendaciones

### Integración con LLM (Ollama)
- **Generación de respuestas naturales**: Utiliza Llama 3.2 1B para crear respuestas conversacionales
- **Extracción de preferencias avanzada**: Analiza consultas complejas en lenguaje natural
- **Personalización**: Adapta el tono y estilo de las respuestas

## 📋 Requisitos Previos

### Software Necesario
1. **Python 3.11+**
2. **Django 5.2.3**
3. **Ollama** con modelo Llama 3.2 1B
4. **Bibliotecas Python**: requests, numpy

### Instalación de Ollama
1. Descarga Ollama desde [https://ollama.ai](https://ollama.ai)
2. Instálalo en tu sistema
3. Ejecuta: `ollama pull llama3.2:1b`
4. Inicia el servidor: `ollama serve`

## 🛠️ Instalación y Configuración

### 1. Clonar e Instalar Dependencias
```bash
cd foodtrail_sucre
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
```bash
cd foodtrail_project
python manage.py makemigrations
python manage.py migrate
```

### 3. Poblar Datos de Ejemplo
```bash
python manage.py populate_data
```

### 4. Verificar Configuración
```bash
cd ..
python check_ollama.py
```

### 5. Iniciar Servidor
```bash
cd foodtrail_project
python manage.py runserver
```

## 🎯 Uso del Chatbot

### Acceso
Visita `http://127.0.0.1:8000/chatbot/` en tu navegador

### Ejemplos de Consultas

#### Búsqueda por Ambiente
- "Quiero un lugar romántico para dos personas en la noche"
- "Busco un restaurante familiar para almorzar"
- "Necesito un lugar tranquilo para una reunión de trabajo"

#### Búsqueda por Comida
- "Recomienda donde comer comida tradicional boliviana"
- "Busco un lugar que sirva pique macho"
- "Quiero probar mondongo chuquisaqueño"

#### Búsqueda por Ocasión
- "Lugar para celebrar un aniversario"
- "Restaurante para una primera cita"
- "Donde llevar a la familia para almorzar"

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### 1. Neural Network (`neural_network.py`)
```python
class NeuralNetworkClassifier:
    - classify_intent()      # Clasifica intenciones del usuario
    - extract_features()     # Extrae características del texto
    - analyze_message()      # Análisis completo del mensaje
```

#### 2. LLM Client (`llm_client.py`)
```python
class OllamaClient:
    - generate_response()           # Genera respuestas conversacionales
    - extract_preferences()         # Extrae preferencias con IA
    - generate_recommendation_text() # Crea texto de recomendación
```

#### 3. Recommendation Engine (`recommendation_engine.py`)
```python
class RecommendationEngine:
    - find_establishments()        # Busca establecimientos relevantes
    - calculate_establishment_score() # Calcula puntuación de relevancia
    - format_establishment_data()  # Formatea datos para respuesta
```

#### 4. Models (`models.py`)
- `ChatSession`: Gestiona sesiones de chat
- `ChatMessage`: Almacena mensajes y recomendaciones
- `UserPreference`: Guarda preferencias del usuario

### Flujo de Procesamiento

1. **Recepción del Mensaje**
   - El usuario envía un mensaje a través de la interfaz web
   - Se crea o recupera la sesión de chat

2. **Análisis con Red Neuronal**
   - Clasificación de la intención del mensaje
   - Extracción de entidades y características
   - Determinación de confianza en la clasificación

3. **Procesamiento con LLM**
   - Si la confianza es baja, se usa Ollama para análisis adicional
   - Extracción de preferencias más detalladas
   - Generación de contexto conversacional

4. **Motor de Recomendaciones**
   - Búsqueda en la base de datos de establecimientos
   - Cálculo de puntuaciones de relevancia
   - Selección de las mejores recomendaciones

5. **Generación de Respuesta**
   - Creación de respuesta personalizada con LLM
   - Formateo de recomendaciones con detalles
   - Envío de respuesta al usuario

## 🔧 Configuración Avanzada

### Personalizar el LLM
En `llm_client.py`, puedes modificar:
```python
class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3.2:1b"):
        # Cambiar modelo o URL según tu configuración
```

### Ajustar la Red Neuronal
En `neural_network.py`, puedes personalizar:
```python
self.intent_keywords = {
    # Agregar nuevas intenciones y palabras clave
}

self.feature_patterns = {
    # Definir nuevos patrones de características
}
```

### Modificar Algoritmo de Recomendaciones
En `recommendation_engine.py`:
```python
self.establishment_weights = {
    'exact_match': 3.0,      # Peso para coincidencias exactas
    'partial_match': 1.5,    # Peso para coincidencias parciales
    'related_match': 1.0,    # Peso para coincidencias relacionadas
    'default': 0.5           # Peso base
}
```

## 📊 APIs Disponibles

### Endpoints del Chatbot
- `GET /chatbot/` - Interfaz del chat
- `POST /chatbot/api/message/` - Enviar mensaje al chatbot
- `GET /chatbot/api/history/<session_id>/` - Obtener historial de chat
- `GET /chatbot/api/health/` - Verificar estado del sistema

### Ejemplo de Uso de API
```javascript
fetch('/chatbot/api/message/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "Busco un lugar romántico",
        session_id: "session-123"
    })
})
```

## 🐛 Resolución de Problemas

### Ollama No Conecta
```bash
# Verificar que Ollama esté corriendo
ollama serve

# Verificar modelos instalados
ollama list

# Instalar modelo si no existe
ollama pull llama3.2:1b
```

### Error de Migraciones
```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

### Problemas de Dependencias
```bash
pip install -r requirements.txt --upgrade
```

## 📈 Métricas y Monitoreo

El sistema registra automáticamente:
- Intenciones clasificadas y niveles de confianza
- Preferencias extraídas de usuarios
- Recomendaciones generadas
- Sesiones de chat y duración
- Errores y problemas de conectividad

## 🔮 Futuras Mejoras

1. **Entrenamiento Continuo**: Mejorar la red neuronal con datos reales de usuarios
2. **Integración con APIs**: Conectar con APIs de mapas y reviews
3. **Soporte Multiidioma**: Agregar soporte para idiomas adicionales
4. **Análisis de Sentimientos Avanzado**: Implementar modelos más sofisticados
5. **Recomendaciones Colaborativas**: Sistema de filtrado colaborativo

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs de Django
2. Ejecuta `python check_ollama.py` para diagnósticos
3. Verifica que todos los servicios estén corriendo

¡Tu chatbot FoodTrail AI está listo para ayudar a los usuarios a descubrir los mejores sabores de Sucre! 🍽️🤖
