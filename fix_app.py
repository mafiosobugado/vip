from app import app, database
from werkzeug.security import generate_password_hash
import traceback
import sys

def main():
    """Main function to initialize the application safely"""
    print("🚀 Iniciando configuração da aplicação...")
    
    # Inicializar o banco dentro do contexto da aplicação
    with app.app_context():
        try:
            # Inicializar banco
            print("📋 Inicializando banco de dados...")
            database.init_db()
            print("✅ Banco inicializado com sucesso")
            
            # Criar usuário teste se não existir
            print("👤 Criando usuário admin...")
            try:
                database.create_user('admin', generate_password_hash('123456'))
                print("✅ Usuário admin criado com sucesso")
            except Exception as e:
                print(f"ℹ️ Usuário admin: {str(e)}")
                
            # Criar alguns executivos se não existirem
            print("👔 Criando executivos...")
            try:
                database.create_executive('João Silva', 'CRÍTICO')
                database.create_executive('Maria Santos', 'MÉDIO')  
                database.create_executive('Pedro Oliveira', 'BAIXO')
                print("✅ Executivos criados com sucesso")
            except Exception as e:
                print(f"ℹ️ Executivos: {str(e)}")
                
            # Criar alguns itens
            print("📝 Criando itens de exemplo...")
            try:
                executives = database.get_all_executives()
                print(f"📊 Encontrados {len(executives)} executivos")
                
                if executives and len(executives) >= 2:
                    database.create_item(
                        executives[0][0], 'Item Crítico', 'Descrição crítica', 
                        'NEGATIVO', 'CRÍTICO', 'PENDENTE', '2025-07-22'
                    )
                    database.create_item(
                        executives[1][0], 'Item Médio', 'Descrição média', 
                        'POSITIVO', 'MÉDIO', 'PENDENTE', '2025-07-22'
                    )
                    print("✅ Itens criados com sucesso")
                else:
                    print("⚠️ Não há executivos suficientes para criar itens")
                    
            except Exception as e:
                print(f"❌ Erro ao criar itens: {str(e)}")
                traceback.print_exc()
                
            print("🎉 Configuração da aplicação concluída!")
            return True
            
        except Exception as e:
            print(f"❌ Erro crítico ao configurar aplicação: {str(e)}")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✨ Script executado com sucesso!")
            sys.exit(0)
        else:
            print("💥 Script falhou!")
            sys.exit(1)
    except Exception as e:
        print(f"🚨 Erro fatal: {str(e)}")
        traceback.print_exc()
        sys.exit(1)