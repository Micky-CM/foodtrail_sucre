"""
Script para configurar las API keys de LLM
"""

def setup_api_keys():
    print("🔧 Configuración de APIs de LLM para FoodTrail AI")
    print("=" * 50)
    
    print("\n📋 Opciones disponibles:")
    print("1. Groq (Recomendado - Gratuito)")
    print("   - Modelos: Llama 3, Mixtral")
    print("   - Límite: 6,000 tokens/minuto gratis")
    print("   - Registro: https://console.groq.com/")
    
    print("\n2. OpenAI (De pago)")
    print("   - Modelos: GPT-3.5, GPT-4")
    print("   - Costo: $0.002/1K tokens")
    print("   - Registro: https://platform.openai.com/")
    
    print("\n3. Modo Fallback (Sin API)")
    print("   - Respuestas básicas predefinidas")
    print("   - No requiere configuración")
    
    choice = input("\n¿Qué opción prefieres? (1/2/3): ").strip()
    
    env_content = ""
    
    if choice == "1":
        print("\n🔑 Configuración de Groq:")
        print("1. Ve a https://console.groq.com/")
        print("2. Regístrate gratis")
        print("3. Ve a 'API Keys' y crea una nueva")
        print("4. Copia la API key")
        
        api_key = input("\nPega tu Groq API key aquí: ").strip()
        if api_key:
            env_content = f"""# Configuración de LLM para FoodTrail AI
GROQ_API_KEY={api_key}
LLM_PROVIDER=groq
"""
        else:
            env_content = """# Configuración de LLM para FoodTrail AI (Modo Fallback)
LLM_PROVIDER=fallback
"""
    
    elif choice == "2":
        print("\n🔑 Configuración de OpenAI:")
        print("1. Ve a https://platform.openai.com/")
        print("2. Regístrate y agrega método de pago")
        print("3. Ve a 'API Keys' y crea una nueva")
        print("4. Copia la API key")
        
        api_key = input("\nPega tu OpenAI API key aquí: ").strip()
        if api_key:
            env_content = f"""# Configuración de LLM para FoodTrail AI
OPENAI_API_KEY={api_key}
LLM_PROVIDER=openai
"""
        else:
            env_content = """# Configuración de LLM para FoodTrail AI (Modo Fallback)
LLM_PROVIDER=fallback
"""
    
    else:
        env_content = """# Configuración de LLM para FoodTrail AI (Modo Fallback)
LLM_PROVIDER=fallback
"""
    
    # Escribir archivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ Configuración guardada en .env")
    
    # Probar la configuración
    print("\n🧪 Probando configuración...")
    try:
        import os
        import sys
        sys.path.append('.')
        
        from dotenv import load_dotenv
        load_dotenv()
        
        from chatbot.online_llm_client import OnlineLLMClient
        
        client = OnlineLLMClient()
        print(f"✅ Cliente creado - Proveedor: {client.provider}, Modelo: {client.model}")
        
        if client.check_connection():
            print("✅ Conexión exitosa")
            
            # Prueba básica
            response = client.generate_response("Hola")
            print(f"✅ Respuesta de prueba: {response[:100]}...")
            
            print("\n🎉 ¡Todo configurado correctamente!")
            print("💻 Tu chatbot está listo para usar en: http://127.0.0.1:8000/chatbot/")
        else:
            print("⚠️  Cliente creado pero sin conexión - funcionará en modo fallback")
    
    except Exception as e:
        print(f"⚠️  Error en la prueba: {e}")
        print("💡 Funcionará en modo fallback")
    
    print("\n📋 Para iniciar el chatbot:")
    print("1. cd foodtrail_project")
    print("2. python manage.py runserver")
    print("3. Ve a http://127.0.0.1:8000/chatbot/")

if __name__ == "__main__":
    setup_api_keys()
