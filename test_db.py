import sqlite3
import os

try:
    # Verificar se o arquivo de banco existe
    if os.path.exists('site.db'):
        print("✅ Arquivo site.db existe")
        
        # Tentar conectar e verificar tabelas
        conn = sqlite3.connect('site.db')
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tabelas encontradas: {tables}")
        
        conn.close()
    else:
        print("❌ Arquivo site.db não existe")
        
except Exception as e:
    print(f"❌ Erro ao verificar banco: {e}")