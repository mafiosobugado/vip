import traceback

try:
    from app import app
    print("✅ Import do app funcionou")
    
    with app.app_context():
        print("✅ Contexto da aplicação funcionou")
        
        # Testar rota simples
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Rota / retornou: {response.status_code}")
            
        # Vou ler o arquivo database.py para ver as funções disponíveis
        with open('database.py', 'r', encoding='utf-8') as f:
            content = f.read()
            print("📋 Conteúdo do database.py:")
            print(content[:2000])  # Primeiros 2000 caracteres
            
except Exception as e:
    print(f"❌ Erro encontrado: {e}")
    traceback.print_exc()