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
            image_filename TEXT, -- Nome do arquivo de imagem (opcional) - mantido para compatibilidade
            FOREIGN KEY (executive_id) REFERENCES executives (id) ON DELETE CASCADE
        );
    ''')

    # Tabela de Imagens dos Itens (múltiplas imagens por item)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            description TEXT,
            upload_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
        );
    ''')

    # Tabela de Alertas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL, -- CRITICO, AVISO, INFO
            related_item_id INTEGER,
            related_executive_id INTEGER,
            is_read BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (related_item_id) REFERENCES items (id) ON DELETE SET NULL,
            FOREIGN KEY (related_executive_id) REFERENCES executives (id) ON DELETE SET NULL
        );
    ''')

    # Tabela de Auditoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            related_table TEXT,
            related_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    
    # Adicionar coluna image_filename se não existir (para compatibilidade com bancos existentes)
    try:
        cursor.execute('ALTER TABLE items ADD COLUMN image_filename TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        # Coluna já existe, ignorar erro
        pass
    
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
def add_item(executive_id, title, description, item_type, severity, status, identified_date, image_filename=None):
    conn = get_db_connection()
    conn.execute('INSERT INTO items (executive_id, title, description, type, severity, status, identified_date, image_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (executive_id, title, description, item_type, severity, status, identified_date, image_filename))
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

def update_item(item_id, executive_id, title, description, item_type, severity, status, identified_date, image_filename=None):
    conn = get_db_connection()
    if image_filename is not None:
        conn.execute('UPDATE items SET executive_id = ?, title = ?, description = ?, type = ?, severity = ?, status = ?, identified_date = ?, image_filename = ? WHERE id = ?',
                     (executive_id, title, description, item_type, severity, status, identified_date, image_filename, item_id))
    else:
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
    count = conn.execute("SELECT COUNT(*) FROM items WHERE status = 'PENDENTE' AND (severity = 'CRITICA' OR severity = 'CRÍTICA')").fetchone()[0]
    conn.close()
    return count

def get_average_severity_score():
    conn = get_db_connection()
    # Mapear severidades para valores numéricos para calcular média
    severity_map = {'BAIXA': 1, 'MEDIA': 2, 'MÉDIA': 2, 'ALTA': 3, 'CRITICA': 4, 'CRÍTICA': 4}
    reverse_map = {1: 'BAIXA', 2: 'MEDIA', 3: 'ALTA', 4: 'CRITICA'}
    
    results = conn.execute('SELECT severity FROM items').fetchall()
    conn.close()
    
    if not results:
        return 'BAIXA'
    
    total_score = 0
    count = 0
    for row in results:
        severity = row[0]
        if severity in severity_map:
            total_score += severity_map[severity]
            count += 1
    
    if count == 0:
        return 'BAIXA'
    
    avg_score = round(total_score / count)
    return reverse_map.get(avg_score, 'BAIXA')

def get_treated_items_last_30_days_count():
    conn = get_db_connection()
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    count = conn.execute("SELECT COUNT(*) FROM items WHERE status = 'TRATADO' AND identified_date >= ?", (thirty_days_ago.isoformat(),)).fetchone()[0]
    conn.close()
    return count

def get_severity_distribution_data():
    conn = get_db_connection()
    # Garante que todos os níveis de severidade sejam considerados, mesmo que com contagem 0
    levels = ['BAIXA', 'MEDIA', 'MÉDIA', 'ALTA', 'CRITICA', 'CRÍTICA']
    distribution = {'BAIXA': 0, 'MEDIA': 0, 'ALTA': 0, 'CRITICA': 0}

    results = conn.execute('SELECT severity, COUNT(*) FROM items GROUP BY severity').fetchall()
    conn.close()

    for row in results:
        level = row[0]
        count = row[1]
        # Normalizar as variações com e sem acento
        if level in ['MEDIA', 'MÉDIA']:
            distribution['MEDIA'] += count
        elif level in ['CRITICA', 'CRÍTICA']:
            distribution['CRITICA'] += count
        elif level in distribution:
            distribution[level] = count
    
    # Remover as chaves temporárias se não foram usadas
    final_distribution = {k: v for k, v in distribution.items() if k in ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']}
    return final_distribution

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

# --- Funções para imagens múltiplas ---
def add_item_image(item_id, filename, description=None):
    """Adiciona uma imagem a um item."""
    conn = get_db_connection()
    conn.execute('INSERT INTO item_images (item_id, filename, description, upload_date) VALUES (?, ?, ?, ?)',
                 (item_id, filename, description, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_item_images(item_id):
    """Obtém todas as imagens de um item."""
    conn = get_db_connection()
    images = conn.execute('SELECT * FROM item_images WHERE item_id = ? ORDER BY upload_date', (item_id,)).fetchall()
    conn.close()
    return images

def delete_item_image(image_id):
    """Remove uma imagem específica."""
    conn = get_db_connection()
    # Primeiro obtém o nome do arquivo para deletar fisicamente
    image = conn.execute('SELECT filename FROM item_images WHERE id = ?', (image_id,)).fetchone()
    if image:
        conn.execute('DELETE FROM item_images WHERE id = ?', (image_id,))
        conn.commit()
        conn.close()
        return image['filename']
    conn.close()
    return None

def update_item_image_description(image_id, description):
    """Atualiza a descrição de uma imagem."""
    conn = get_db_connection()
    conn.execute('UPDATE item_images SET description = ? WHERE id = ?', (description, image_id))
    conn.commit()
    conn.close()

# --- Funções para ALERTAS ---

def add_alert(title, description, alert_type, related_item_id=None, related_executive_id=None):
    """Adiciona um novo alerta."""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO alerts (title, description, type, related_item_id, related_executive_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, alert_type, related_item_id, related_executive_id, datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')))
    conn.commit()
    conn.close()

def get_all_alerts():
    """Obtém todos os alertas ordenados por data de criação (mais recentes primeiro)."""
    conn = get_db_connection()
    alerts = conn.execute('''
        SELECT a.*, e.name as executive_name, i.title as item_title
        FROM alerts a
        LEFT JOIN executives e ON a.related_executive_id = e.id
        LEFT JOIN items i ON a.related_item_id = i.id
        ORDER BY a.created_at DESC
    ''').fetchall()
    conn.close()
    return alerts

def get_recent_alerts(limit=5):
    """Obtém os alertas mais recentes para o dropdown de notificações."""
    conn = get_db_connection()
    alerts = conn.execute('''
        SELECT a.*, e.name as executive_name, i.title as item_title
        FROM alerts a
        LEFT JOIN executives e ON a.related_executive_id = e.id
        LEFT JOIN items i ON a.related_item_id = i.id
        ORDER BY a.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(alert) for alert in alerts]

def get_unread_alerts_count():
    """Conta alertas não lidos."""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as count FROM alerts WHERE is_read = 0').fetchone()
    conn.close()
    return count['count'] if count else 0

def mark_alert_as_read(alert_id):
    """Marca um alerta como lido."""
    conn = get_db_connection()
    conn.execute('UPDATE alerts SET is_read = 1 WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()

def delete_alert(alert_id):
    """Remove um alerta."""
    conn = get_db_connection()
    conn.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()

# --- Funções para AUDITORIA ---

def add_audit_log(user, action, details, related_table=None, related_id=None):
    """Adiciona um registro de auditoria."""
    conn = get_db_connection()
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    conn.execute('''
        INSERT INTO audit_log (timestamp, user, action, details, related_table, related_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, user, action, details, related_table, related_id))
    conn.commit()
    conn.close()

def get_all_audit_logs():
    """Obtém todos os logs de auditoria ordenados por data (mais recentes primeiro)."""
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT * FROM audit_log
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return logs

def create_sample_audit_logs():
    """Cria alguns logs de auditoria de exemplo para demonstração."""
    try:
        # Simular algumas ações do sistema
        add_audit_log('Analista', 'Criou item identificado', 'Credencial encontrada para Carlos Andrade', 'items', 1)
        add_audit_log('Sistema', 'Atualizou score de risco', 'Score de Carlos Andrade alterado para 9.5', 'executives', 1)
        add_audit_log('Analista', 'Marcou item como tratado', 'Telefone de Carlos Andrade - ID: 3', 'items', 3)
        add_audit_log('Analista', 'Criou item identificado', 'Email de Beatriz Lima adicionado', 'items', 2)
        add_audit_log('Sistema', 'Detectou nova exposição', 'Endereço de Sofia Costa encontrado', 'items', 4)
        return True
    except Exception as e:
        print(f"Erro ao criar logs de auditoria de exemplo: {e}")
        return False

def create_sample_alerts():
    """Cria alertas de exemplo para demonstração."""
    sample_alerts = [
        ("Nova credencial encontrada", "Credencial de Carlos Andrade encontrada em breach recente", "CRITICO", None, None),
        ("Score de risco aumentou", "Score de risco de Carlos Andrade aumentou para 9.5", "AVISO", None, None),
        ("Item tratado com sucesso", "Telefone de Carlos Andrade foi marcado como tratado", "INFO", None, None),
        ("Sistema atualizado", "Sistema VIP Monitoring foi atualizado para versão 2.1", "INFO", None, None),
        ("Novo executivo adicionado", "Maria Silva foi adicionada ao sistema de monitoramento", "INFO", None, None)
    ]
    
    for title, description, alert_type, item_id, exec_id in sample_alerts:
        add_alert(title, description, alert_type, item_id, exec_id)