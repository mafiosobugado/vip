import sqlite3
import datetime

DATABASE = 'site.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Isso permite acessar colunas por nome
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de Usuários para autenticação
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    # Tabela de Executivos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS executives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT,
            department TEXT,
            risk_score REAL DEFAULT 0.0,
            risk_level TEXT DEFAULT 'NENHUM'
        );
    ''')

    # Tabela de Itens Identificados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            executive_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL, -- Ex: CREDENTIAL, DOCUMENTO, TELEFONE, EMAIL, ENDERECO
            severity TEXT NOT NULL, -- Ex: BAIXA, MEDIA, ALTA, CRITICA
            status TEXT NOT NULL, -- Ex: PENDENTE, TRATADO, IGNORADO
            identified_date TEXT NOT NULL, -- Data no formato YYYY-MM-DD
            FOREIGN KEY (executive_id) REFERENCES executives (id) ON DELETE CASCADE
        );
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados inicializado e tabelas criadas (se não existiam).")

# --- Funções para a tabela USERS ---
class User:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['password'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['password'])
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['password'])
        return None

    @staticmethod
    def create(username, email, password_hash):
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Usuário ou email já existem
        finally:
            conn.close()

# --- Funções para a tabela EXECUTIVES ---
def add_executive(name, email, role, department, risk_score, risk_level):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO executives (name, email, role, department, risk_score, risk_level) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, email, role, department, risk_score, risk_level))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Email já existe
    finally:
        conn.close()

def get_all_executives():
    conn = get_db_connection()
    executives = conn.execute('SELECT * FROM executives').fetchall()
    conn.close()
    return executives

def get_executive_by_id(executive_id):
    conn = get_db_connection()
    executive = conn.execute('SELECT * FROM executives WHERE id = ?', (executive_id,)).fetchone()
    conn.close()
    return executive

def update_executive(executive_id, name, email, role, department, risk_score, risk_level):
    conn = get_db_connection()
    try:
        conn.execute('UPDATE executives SET name = ?, email = ?, role = ?, department = ?, risk_score = ?, risk_level = ? WHERE id = ?',
                     (name, email, role, department, risk_score, risk_level, executive_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Email já existe
    finally:
        conn.close()

def delete_executive(executive_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM executives WHERE id = ?', (executive_id,))
    conn.commit()
    conn.close()

# --- Funções para a tabela ITEMS ---
def add_item(executive_id, title, description, item_type, severity, status, identified_date):
    conn = get_db_connection()
    conn.execute('INSERT INTO items (executive_id, title, description, type, severity, status, identified_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (executive_id, title, description, item_type, severity, status, identified_date))
    conn.commit()
    conn.close()

def get_all_items():
    conn = get_db_connection()
    items = conn.execute('SELECT i.*, e.name as executive_name FROM items i JOIN executives e ON i.executive_id = e.id ORDER BY i.identified_date DESC').fetchall()
    conn.close()
    return items

def get_item_by_id(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT i.*, e.name as executive_name FROM items i JOIN executives e ON i.executive_id = e.id WHERE i.id = ?', (item_id,)).fetchone()
    conn.close()
    return item

def update_item(item_id, executive_id, title, description, item_type, severity, status, identified_date):
    conn = get_db_connection()
    conn.execute('UPDATE items SET executive_id = ?, title = ?, description = ?, type = ?, severity = ?, status = ?, identified_date = ? WHERE id = ?',
                 (executive_id, title, description, item_type, severity, status, identified_date, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

# --- Funções para Dados do Dashboard ---
def get_total_executives_count():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM executives').fetchone()[0]
    conn.close()
    return count

def get_critical_pending_items_count():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM items WHERE status = 'PENDENTE' AND severity = 'CRITICA'").fetchone()[0]
    conn.close()
    return count

def get_average_risk_score_value():
    conn = get_db_connection()
    avg_score = conn.execute('SELECT AVG(risk_score) FROM executives').fetchone()[0]
    conn.close()
    return round(avg_score, 2) if avg_score is not None else 0.0

def get_treated_items_last_30_days_count():
    conn = get_db_connection()
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    count = conn.execute("SELECT COUNT(*) FROM items WHERE status = 'TRATADO' AND identified_date >= ?", (thirty_days_ago.isoformat(),)).fetchone()[0]
    conn.close()
    return count

def get_risk_level_distribution_data():
    conn = get_db_connection()
    # Garante que todos os níveis de risco sejam considerados, mesmo que com contagem 0
    levels = ['NENHUM', 'BAIXO', 'MÉDIO', 'ALTO', 'CRÍTICO']
    distribution = {level: 0 for level in levels}

    results = conn.execute('SELECT risk_level, COUNT(*) FROM executives GROUP BY risk_level').fetchall()
    conn.close()

    for row in results:
        level = row[0]
        count = row[1]
        if level in distribution:
            distribution[level] = count
    return distribution

def get_identified_items_trend_data(num_weeks=8):
    conn = get_db_connection()
    today = datetime.date.today()
    dates = []
    counts = []

    for i in range(num_weeks - 1, -1, -1):
        date_n_weeks_ago = today - datetime.timedelta(weeks=i)
        dates.append(date_n_weeks_ago.isoformat())

        count = conn.execute('SELECT COUNT(*) FROM items WHERE identified_date = ?', (date_n_weeks_ago.isoformat(),)).fetchone()[0]
        counts.append(count)

    conn.close()
    return {'dates': dates, 'counts': counts}