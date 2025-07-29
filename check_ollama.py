"""
Script para verificar la instalación y configuración de Ollama
"""
import requests
import json

def check_ollama():
    """Verifica si Ollama está corriendo y configurado correctamente"""
    
    print("🔍 Verificando Ollama...")
    
    try:
        # Verificar si Ollama está corriendo
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama está corriendo correctamente")
            
            # Verificar modelos disponibles
            models = response.json().get('models', [])
            print(f"📊 Modelos disponibles: {len(models)}")
            
            for model in models:
                print(f"   - {model['name']}")
            
            # Verificar si llama3.2:1b está disponible
            llama_models = [m for m in models if 'llama3.2' in m['name'] or 'llama' in m['name']]
            
            if llama_models:
                print("✅ Modelo Llama encontrado")
                return True
            else:
                print("⚠️  Modelo Llama3.2:1b no encontrado")
                print("💡 Para instalarlo, ejecuta: ollama pull llama3.2:1b")
                return False
                
        else:
            print(f"❌ Error: Ollama respondió con código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a Ollama")
        print("💡 Asegúrate de que Ollama esté corriendo:")
        print("   - Inicia Ollama desde el menú de inicio")
        print("   - O ejecuta 'ollama serve' en una terminal")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_chat():
    """Prueba básica del chat con Ollama"""
    print("\n🧪 Probando chat con Ollama...")
    
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.2:1b",
            "prompt": "Hola, ¿puedes recomendarme un restaurante?",
            "stream": False,
            "options": {
                "num_predict": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat funcionando correctamente")
            print(f"📝 Respuesta de prueba: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en chat: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de chat: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando configuración del Chatbot FoodTrail")
    print("=" * 50)
    
    ollama_ok = check_ollama()
    
    if ollama_ok:
        chat_ok = test_chat()
        
        if chat_ok:
            print("\n🎉 ¡Todo está configurado correctamente!")
            print("💻 Tu chatbot está listo para usar en: http://127.0.0.1:8000/chatbot/")
        else:
            print("\n⚠️  Ollama está corriendo pero hay problemas con el chat")
    else:
        print("\n❌ Hay problemas con la configuración de Ollama")
    
    print("\n📋 Instrucciones para usar el chatbot:")
    print("1. Asegúrate de que Ollama esté corriendo")
    print("2. Visita http://127.0.0.1:8000/chatbot/ en tu navegador")
    print("3. Prueba consultas como:")
    print("   - 'Quiero un lugar romántico para dos personas'")
    print("   - 'Busco comida tradicional boliviana'")
    print("   - 'Recomienda un restaurante familiar'")

if __name__ == "__main__":
    main()
