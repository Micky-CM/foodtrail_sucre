#!/usr/bin/env python3
import os
import django
import sys

# Configurar Django
sys.path.append(r'C:\xampp\htdocs\Proyecto_Gastro\foodtrail_sucre\foodtrail_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodtrail_project.settings')
django.setup()

from chatbot.llm_client import OllamaClient

def test_ollama():
    print("🚀 Probando conexión con Ollama...")
    
    try:
        # Crear cliente
        client = OllamaClient()
        print(f"✅ Cliente creado - URL: {client.base_url}, Modelo: {client.model}")
        
        # Probar conexión básica
        response = client.generate_response("Hola, ¿cómo estás?")
        print(f"✅ Respuesta recibida: {response[:100]}...")
        
        # Probar extracción de preferencias
        preferences = client.extract_preferences("Quiero un restaurante romántico para dos personas")
        print(f"✅ Preferencias extraídas: {preferences}")
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ollama()
