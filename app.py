from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import database # Importe seu módulo de banco de dados
import datetime
import traceback
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui_para_producao' # MUDE ISSO EM PRODUÇÃO!
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30) # Exemplo: sessão dura 30 minutos
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

# Criar diretório de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função helper para logging de auditoria
def log_user_action(action, details, related_table=None, related_id=None):
    """Registra uma ação do usuário no log de auditoria."""
    try:
        username = current_user.username if current_user.is_authenticated else 'Sistema'
        database.add_audit_log(username, action, details, related_table, related_id)
    except Exception as e:
        print(f"Erro ao registrar log de auditoria: {e}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Nome da função de view para redirecionar usuários não autenticados

# Define a função de user_loader para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        return database.User.get(user_id)
    except Exception as e:
        print(f"Erro ao carregar usuário {user_id}: {e}")
        return None

# --- ERROR HANDLERS ---
@app.errorhandler(500)
def internal_error(error):
    print(f"Erro interno do servidor: {error}")
    traceback.print_exc()
    return render_template('error.html', error="Erro interno do servidor. Verifique os logs."), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Página não encontrada."), 404

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = database.User.get_by_username(username)

            if user and check_password_hash(user.password, password):
                login_user(user, remember=True) # remember=True cria uma sessão permanente
                log_user_action('Login realizado', f'Usuário {username} fez login no sistema')
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('dashboard'))
            else:
                log_user_action('Tentativa de login falhada', f'Tentativa de login falhada para usuário: {username}')
                flash('Nome de usuário ou senha inválidos.', 'danger')
        return render_template('login.html')
    except Exception as e:
        print(f"Erro na rota login: {e}")
        traceback.print_exc()
        flash('Erro interno. Tente novamente.', 'danger')
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('As senhas não coincidem!', 'danger')
                return render_template('register.html', username=username, email=email)

            hashed_password = generate_password_hash(password, method='scrypt') # Método seguro

            if database.User.create(username, email, hashed_password):
                flash('Conta criada com sucesso! Faça login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Nome de usuário ou email já existem.', 'danger')
                return render_template('register.html', username=username, email=email)
        return render_template('register.html')
    except Exception as e:
        print(f"Erro na rota register: {e}")
        traceback.print_exc()
        flash('Erro interno. Tente novamente.', 'danger')
        return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    try:
        username = current_user.username if current_user.is_authenticated else 'Usuário desconhecido'
        log_user_action('Logout realizado', f'Usuário {username} fez logout do sistema')
        logout_user()
        flash('Você foi desconectado.', 'info')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Erro na rota logout: {e}")
        return redirect(url_for('login'))

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Erro na rota index: {e}")
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        total_executives = database.get_total_executives_count()
        critical_pending_items = database.get_critical_pending_items_count()
        average_severity = database.get_average_severity_score()
        treated_items_last_30_days = database.get_treated_items_last_30_days_count()
        severity_distribution = database.get_severity_distribution_data()
        identified_items_trend = database.get_identified_items_trend_data()

        return render_template(
            'dashboard.html',
            total_executives=total_executives,
            critical_pending_items=critical_pending_items,
            average_severity=average_severity,
            treated_items_last_30_days=treated_items_last_30_days,
            severity_distribution=severity_distribution,
            identified_items_trend=identified_items_trend,
            active_page='dashboard'
        )
    except Exception as e:
        print(f"Erro na rota dashboard: {e}")
        traceback.print_exc()
        flash('Erro ao carregar dashboard.', 'danger')
        return render_template('dashboard.html', 
                             total_executives=0, 
                             critical_pending_items=0,
                             average_severity='BAIXA',
                             treated_items_last_30_days=0,
                             severity_distribution={},
                             identified_items_trend={'dates': [], 'counts': []},
                             active_page='dashboard')

@app.route('/executives')
@login_required
def executives():
    all_executives = database.get_all_executives()
    return render_template('executives.html', executives=all_executives, active_page='executives')

@app.route('/add_executive', methods=['GET', 'POST'])
@login_required
def add_executive():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form.get('role')
        department = request.form.get('department')
        # Usar valores padrão para risk_score e risk_level
        risk_score = 0.0
        risk_level = 'NENHUM'

        if database.add_executive(name, email, role, department, risk_score, risk_level):
            # Registrar log de auditoria
            log_user_action('Executivo criado', f'Executivo {name} ({email}) adicionado ao sistema', 'executives')
            
            # Criar alerta de novo executivo
            database.add_alert(
                "👤 Novo executivo adicionado",
                f"Executivo '{name}' foi adicionado ao sistema. Cargo: {role or 'Não informado'}, Departamento: {department or 'Não informado'}",
                "INFO"
            )
            
            flash('Executivo adicionado com sucesso!', 'success')
            return redirect(url_for('executives'))
        else:
            log_user_action('Falha ao criar executivo', f'Tentativa de adicionar executivo {name} ({email}) falhou - email já existe')
            flash('Erro: Já existe um executivo com este e-mail.', 'danger')
    return render_template('add_edit_executive.html', executive=None, active_page='executives')


@app.route('/edit_executive/<int:executive_id>', methods=['GET', 'POST'])
@login_required
def edit_executive(executive_id):
    executive = database.get_executive_by_id(executive_id)
    if not executive:
        flash('Executivo não encontrado.', 'danger')
        return redirect(url_for('executives'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form.get('role')
        department = request.form.get('department')
        # Manter os valores existentes de risk_score e risk_level
        risk_score = executive['risk_score']
        risk_level = executive['risk_level']

        if database.update_executive(executive_id, name, email, role, department, risk_score, risk_level):
            log_user_action('Executivo atualizado', f'Executivo {name} (ID: {executive_id}) foi atualizado', 'executives', executive_id)
            flash('Executivo atualizado com sucesso!', 'success')
            return redirect(url_for('executives'))
        else:
            log_user_action('Falha ao atualizar executivo', f'Tentativa de atualizar executivo {name} (ID: {executive_id}) falhou - email já existe')
            flash('Erro: Já existe outro executivo com este e-mail.', 'danger')
            return render_template('add_edit_executive.html', executive=executive, active_page='executives') # Renderiza com os dados originais
    return render_template('add_edit_executive.html', executive=executive, active_page='executives')

@app.route('/delete_executive/<int:executive_id>', methods=['POST'])
@login_required
def delete_executive(executive_id):
    # Obter dados do executivo antes de excluir para o log
    executive = database.get_executive_by_id(executive_id)
    executive_name = executive['name'] if executive else f'ID: {executive_id}'
    
    database.delete_executive(executive_id)
    log_user_action('Executivo excluído', f'Executivo {executive_name} foi excluído do sistema', 'executives', executive_id)
    flash('Executivo excluído com sucesso!', 'success')
    return redirect(url_for('executives'))


@app.route('/items')
@login_required
def items():
    all_executives = database.get_all_executives() # Para o filtro de executivos
    all_items = database.get_all_items()
    
    # Converter sqlite3.Row para dict e adicionar informação sobre múltiplas imagens
    items_list = []
    for item in all_items:
        # Converter Row para dict
        item_dict = dict(item)
        item_images = database.get_item_images(item_dict['id'])
        item_dict['has_multiple_images'] = len(item_images) > 0
        item_dict['total_images'] = len(item_images) + (1 if item_dict.get('image_filename') else 0)
        items_list.append(item_dict)
    
    return render_template('items.html', items=items_list, executives=all_executives, active_page='items')

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    executives_list = database.get_all_executives() # Para o dropdown
    if request.method == 'POST':
        executive_id = request.form['executive_id']
        title = request.form['title']
        description = request.form.get('description')
        item_type = request.form['type']
        severity = request.form['severity']
        status = request.form['status']
        identified_date = request.form['identified_date']
        
        # Lidar com upload de imagem
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Gerar nome único para o arquivo
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_filename = filename

        database.add_item(executive_id, title, description, item_type, severity, status, identified_date, image_filename)
        
        # Registrar log de auditoria
        executive = database.get_executive_by_id(executive_id)
        executive_name = executive['name'] if executive else f'ID: {executive_id}'
        log_user_action('Item criado', f'Item "{title}" ({item_type}, {severity}) criado para {executive_name}', 'items')
        
        # Criar alertas automáticos baseados na severidade e tipo
        
        if severity == 'CRITICA':
            database.add_alert(
                "🚨 Novo item CRÍTICO identificado",
                f"Item '{title}' de severidade CRÍTICA foi identificado para {executive_name}. Tipo: {item_type}. Requer ação imediata!",
                "CRITICO",
                None,
                executive_id
            )
        elif severity == 'ALTA':
            database.add_alert(
                "⚠️ Item de alta severidade identificado",
                f"Item '{title}' de severidade ALTA foi identificado para {executive_name}. Tipo: {item_type}.",
                "AVISO",
                None,
                executive_id
            )
        
        # Alerta para tipos específicos sensíveis
        if item_type in ['CREDENTIAL', 'DOCUMENTO']:
            database.add_alert(
                f"🔐 {item_type} sensível identificado",
                f"Novo {item_type.lower()} '{title}' foi identificado para {executive_name}. Verificar segurança.",
                "AVISO",
                None,
                executive_id
            )
        
        # Alerta geral para novos itens
        database.add_alert(
            "📋 Novo item adicionado",
            f"Item '{title}' foi adicionado para {executive_name}. Status: {status}, Severidade: {severity}",
            "INFO",
            None,
            executive_id
        )
        
        flash('Item identificado adicionado com sucesso!', 'success')
        return redirect(url_for('items'))
    return render_template('add_edit_item.html', item=None, executives=executives_list, active_page='items')

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = database.get_item_by_id(item_id)
    if not item:
        flash('Item não encontrado.', 'danger')
        return redirect(url_for('items'))

    executives_list = database.get_all_executives() # Para o dropdown
    item_images = database.get_item_images(item_id) # Obter imagens múltiplas
    
    if request.method == 'POST':
        executive_id = request.form['executive_id']
        title = request.form['title']
        description = request.form.get('description')
        item_type = request.form['type']
        severity = request.form['severity']
        status = request.form['status']
        identified_date = request.form['identified_date']
        
        # Lidar com upload de nova imagem
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Remover imagem antiga se existir
                if hasattr(item, 'image_filename') and item['image_filename']:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], item['image_filename'])
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Salvar nova imagem
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_filename = filename
            elif hasattr(item, 'image_filename'):
                # Manter imagem existente se não houver nova
                image_filename = item['image_filename']

        database.update_item(item_id, executive_id, title, description, item_type, severity, status, identified_date, image_filename)
        
        # Registrar log de auditoria
        executive = database.get_executive_by_id(executive_id)
        executive_name = executive['name'] if executive else f'ID: {executive_id}'
        log_user_action('Item atualizado', f'Item "{title}" (ID: {item_id}) atualizado para {executive_name}', 'items', item_id)
        
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('items'))
    return render_template('add_edit_item.html', item=item, executives=executives_list, item_images=item_images, active_page='items')


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    # Obter dados do item antes de excluir para o log
    item = database.get_item_by_id(item_id)
    item_title = item['title'] if item else f'ID: {item_id}'
    
    database.delete_item(item_id)
    log_user_action('Item excluído', f'Item "{item_title}" foi excluído do sistema', 'items', item_id)
    flash('Item excluído com sucesso!', 'success')
    return redirect(url_for('items'))

@app.route('/mark_item_treated/<int:item_id>', methods=['POST'])
@login_required
def mark_item_treated(item_id):
    item = database.get_item_by_id(item_id)
    if item:
        image_filename = item.get('image_filename') if hasattr(item, 'get') else item['image_filename'] if 'image_filename' in item else None
        database.update_item(item_id, item['executive_id'], item['title'], item['description'], item['type'], item['severity'], 'TRATADO', item['identified_date'], image_filename)
        
        # Registrar log de auditoria
        executive = database.get_executive_by_id(item['executive_id'])
        executive_name = executive['name'] if executive else f'ID: {item["executive_id"]}'
        log_user_action('Item marcado como tratado', f'Item "{item["title"]}" de {executive_name} foi marcado como TRATADO', 'items', item_id)
        
        # Criar alerta de sucesso
        database.add_alert(
            "✅ Item tratado com sucesso",
            f"Item '{item['title']}' de {executive_name} foi marcado como TRATADO. Problema resolvido!",
            "INFO",
            item_id,
            item['executive_id']
        )
        
        flash('Item marcado como TRATADO!', 'success')
    else:
        flash('Item não encontrado.', 'danger')
    return redirect(url_for('items'))

@app.route('/mark_item_ignored/<int:item_id>', methods=['POST'])
@login_required
def mark_item_ignored(item_id):
    item = database.get_item_by_id(item_id)
    if item:
        image_filename = item.get('image_filename') if hasattr(item, 'get') else item['image_filename'] if 'image_filename' in item else None
        database.update_item(item_id, item['executive_id'], item['title'], item['description'], item['type'], item['severity'], 'IGNORADO', item['identified_date'], image_filename)
        
        # Registrar log de auditoria
        executive = database.get_executive_by_id(item['executive_id'])
        executive_name = executive['name'] if executive else f'ID: {item["executive_id"]}'
        log_user_action('Item marcado como ignorado', f'Item "{item["title"]}" de {executive_name} foi marcado como IGNORADO', 'items', item_id)
        
        # Criar alerta informativo
        database.add_alert(
            "ℹ️ Item marcado como ignorado",
            f"Item '{item['title']}' de {executive_name} foi marcado como IGNORADO.",
            "INFO",
            item_id,
            item['executive_id']
        )
        
        flash('Item marcado como IGNORADO!', 'info')
    else:
        flash('Item não encontrado.', 'danger')
    return redirect(url_for('items'))


@app.route('/reports')
@login_required
def reports():
    try:
        # Obter estatísticas para a página
        total_executives = len(database.get_all_executives())
        total_items = len(database.get_all_items())
        total_audit_logs = len(database.get_all_audit_logs())
        
        return render_template('reports.html', 
                             active_page='reports',
                             total_executives=total_executives,
                             total_items=total_items,
                             total_audit_logs=total_audit_logs)
    except Exception as e:
        print(f"Erro na rota reports: {e}")
        return render_template('reports.html', 
                             active_page='reports',
                             total_executives=0,
                             total_items=0,
                             total_audit_logs=0)

# --- ROTAS DE EXPORTAÇÃO DE RELATÓRIOS ---

@app.route('/export_report/<report_type>')
@login_required
def export_report(report_type):
    """Exporta relatórios em formato CSV."""
    try:
        import csv
        import io
        from flask import make_response
        
        # Registrar log de auditoria
        log_user_action('Relatório exportado', f'Relatório de {report_type} exportado em CSV')
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == 'executives':
            # Exportar dados dos executivos
            executives = database.get_all_executives()
            writer.writerow(['ID', 'Nome', 'Email', 'Cargo', 'Departamento', 'Score de Risco', 'Nível de Risco'])
            for exec in executives:
                writer.writerow([
                    exec['id'],
                    exec['name'],
                    exec['email'],
                    exec['role'] or '',
                    exec['department'] or '',
                    exec['risk_score'],
                    exec['risk_level']
                ])
                
        elif report_type == 'items':
            # Exportar dados dos itens identificados
            items = database.get_all_items()
            writer.writerow(['ID', 'Executivo', 'Título', 'Descrição', 'Tipo', 'Severidade', 'Status', 'Data Identificação'])
            for item in items:
                writer.writerow([
                    item['id'],
                    item['executive_name'] or 'N/A',
                    item['title'],
                    item['description'] or '',
                    item['type'],
                    item['severity'],
                    item['status'],
                    item['identified_date']
                ])
                
        elif report_type == 'audit':
            # Exportar logs de auditoria
            audit_logs = database.get_all_audit_logs()
            writer.writerow(['ID', 'Data/Hora', 'Usuário', 'Ação', 'Detalhes', 'Tabela Relacionada', 'ID Relacionado'])
            for log in audit_logs:
                writer.writerow([
                    log['id'],
                    log['timestamp'],
                    log['user'],
                    log['action'],
                    log['details'],
                    log['related_table'] or '',
                    log['related_id'] or ''
                ])
        else:
            flash('Tipo de relatório inválido.', 'danger')
            return redirect(url_for('reports'))
        
        # Preparar resposta CSV
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{report_type}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Erro ao exportar relatório {report_type}: {e}")
        flash('Erro ao exportar relatório. Tente novamente.', 'danger')
        return redirect(url_for('reports'))

# --- ROTAS DE ALERTAS ---
@app.route('/alerts')
@login_required
def alerts():
    """Página principal de alertas."""
    try:
        all_alerts = database.get_all_alerts()
        return render_template('alerts.html', alerts=all_alerts, active_page='alerts')
    except Exception as e:
        print(f"Erro na rota alerts: {e}")
        return render_template('alerts.html', alerts=[], active_page='alerts')

@app.route('/mark_alert_read/<int:alert_id>', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Marca um alerta como lido."""
    try:
        database.mark_alert_as_read(alert_id)
        log_user_action('Alerta marcado como lido', f'Alerta ID: {alert_id} foi marcado como lido', 'alerts', alert_id)
        return {'success': True}
    except Exception as e:
        print(f"Erro ao marcar alerta como lido: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/delete_alert/<int:alert_id>', methods=['DELETE'])
@login_required
def delete_alert(alert_id):
    """Remove um alerta."""
    try:
        database.delete_alert(alert_id)
        log_user_action('Alerta excluído', f'Alerta ID: {alert_id} foi excluído do sistema', 'alerts', alert_id)
        return {'success': True}
    except Exception as e:
        print(f"Erro ao deletar alerta: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/get_unread_alerts_count')
@login_required
def get_unread_alerts_count():
    """Retorna o número de alertas não lidos."""
    try:
        count = database.get_unread_alerts_count()
        return {'count': count}
    except Exception as e:
        print(f"Erro ao contar alertas: {e}")
        return {'count': 0}

@app.route('/get_recent_alerts')
@login_required
def get_recent_alerts():
    """Retorna os alertas mais recentes para o dropdown de notificações."""
    try:
        # Buscar os 5 alertas mais recentes
        recent_alerts = database.get_recent_alerts(limit=5)
        
        # Formatar os alertas para o dropdown
        formatted_alerts = []
        for alert in recent_alerts:
            # Calcular tempo relativo
            time_diff = datetime.datetime.now() - datetime.datetime.strptime(alert['created_at'], '%d/%m/%Y, %H:%M:%S')
            
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} dia{'s' if time_diff.days > 1 else ''} atrás"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hora{'s' if hours > 1 else ''} atrás"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} min atrás"
            else:
                time_ago = "Agora"
            
            # Determinar o ícone baseado no tipo
            icon_map = {
                'CRITICO': 'fas fa-exclamation-triangle',
                'AVISO': 'fas fa-exclamation-circle',
                'INFO': 'fas fa-info-circle'
            }
            
            formatted_alerts.append({
                'id': alert['id'],
                'title': alert['title'],
                'description': alert['description'][:80] + '...' if len(alert['description']) > 80 else alert['description'],
                'type': alert['type'],
                'icon': icon_map.get(alert['type'], 'fas fa-bell'),
                'is_read': alert['is_read'],
                'time_ago': time_ago,
                'executive_name': alert.get('executive_name'),
                'item_title': alert.get('item_title')
            })
        
        return {'success': True, 'alerts': formatted_alerts}
    except Exception as e:
        print(f"Erro ao buscar alertas recentes: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/create_sample_alerts', methods=['POST'])
@login_required
def create_sample_alerts():
    """Cria alertas de exemplo para demonstração."""
    try:
        database.create_sample_alerts()
        return {'success': True}
    except Exception as e:
        print(f"Erro ao criar alertas de exemplo: {e}")
        return {'success': False, 'error': str(e)}, 500

# --- Rota para AUDITORIA ---
@app.route('/audit')
@login_required
def audit():
    """Página de auditoria com histórico de alterações."""
    audit_logs = database.get_all_audit_logs()
    return render_template('audit.html', audit_logs=audit_logs, active_page='audit')

@app.route('/create_sample_audit_logs', methods=['POST'])
@login_required
def create_sample_audit_logs():
    """Cria logs de auditoria de exemplo para demonstração."""
    try:
        database.create_sample_audit_logs()
        return {'success': True}
    except Exception as e:
        print(f"Erro ao criar logs de auditoria de exemplo: {e}")
        return {'success': False, 'error': str(e)}, 500

# --- Rotas para imagens múltiplas ---
@app.route('/add_item_image/<int:item_id>', methods=['POST'])
@login_required
def add_item_image(item_id):
    """Adiciona uma nova imagem a um item."""
    try:
        if 'image' not in request.files:
            return {'error': 'Nenhuma imagem enviada'}, 400
        
        file = request.files['image']
        description = request.form.get('description', '')
        
        if file and file.filename != '' and allowed_file(file.filename):
            # Gerar nome único para o arquivo
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Salvar no banco
            database.add_item_image(item_id, filename, description)
            
            # Criar alerta para nova imagem
            item = database.get_item_by_id(item_id)
            if item:
                executive = database.get_executive_by_id(item['executive_id'])
                executive_name = executive['name'] if executive else 'Executivo'
                database.add_alert(
                    "📷 Nova imagem adicionada",
                    f"Nova imagem foi adicionada ao item '{item['title']}' de {executive_name}",
                    "INFO",
                    item_id,
                    item['executive_id']
                )
            
            return {'success': True, 'filename': filename, 'description': description}
        else:
            return {'error': 'Arquivo inválido'}, 400
    except Exception as e:
        print(f"Erro ao adicionar imagem: {e}")
        return {'error': 'Erro interno do servidor'}, 500

@app.route('/delete_item_image/<int:image_id>', methods=['DELETE'])
@login_required
def delete_item_image(image_id):
    """Remove uma imagem específica."""
    try:
        filename = database.delete_item_image(image_id)
        if filename:
            # Remover arquivo físico
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            return {'success': True}
        else:
            return {'error': 'Imagem não encontrada'}, 404
    except Exception as e:
        print(f"Erro ao deletar imagem: {e}")
        return {'error': 'Erro interno do servidor'}, 500

@app.route('/update_image_description/<int:image_id>', methods=['PUT'])
@login_required
def update_image_description(image_id):
    """Atualiza a descrição de uma imagem."""
    try:
        data = request.get_json()
        description = data.get('description', '')
        database.update_item_image_description(image_id, description)
        return {'success': True}
    except Exception as e:
        print(f"Erro ao atualizar descrição: {e}")
        return {'error': 'Erro interno do servidor'}, 500

@app.route('/get_item_images/<int:item_id>')
@login_required
def get_item_images_api(item_id):
    """Retorna todas as imagens de um item em formato JSON."""
    try:
        item = database.get_item_by_id(item_id)
        if not item:
            return {'error': 'Item não encontrado'}, 404
        
        images = []
        
        # Adicionar imagem principal se existir
        if item.get('image_filename'):
            images.append({
                'id': 'main',
                'filename': item['image_filename'],
                'description': 'Imagem principal',
                'url': url_for('static', filename='uploads/' + item['image_filename']),
                'is_main': True
            })
        
        # Adicionar imagens múltiplas
        item_images = database.get_item_images(item_id)
        for img in item_images:
            images.append({
                'id': img['id'],
                'filename': img['filename'],
                'description': img['description'] or 'Sem descrição',
                'url': url_for('static', filename='uploads/' + img['filename']),
                'is_main': False
            })
        
        return {'images': images, 'total': len(images)}
    except Exception as e:
        print(f"Erro ao buscar imagens: {e}")
        return {'error': 'Erro interno do servidor'}, 500

# --- Inicialização do banco de dados ---
try:
    with app.app_context():
        database.init_db()
        print("✅ Banco de dados inicializado com sucesso")
        
        # Criar alerta de sistema iniciado
        database.add_alert(
            "🚀 Sistema VIP Monitoring iniciado",
            f"Sistema iniciado com sucesso em {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}. Monitoramento ativo!",
            "INFO"
        )
        
except Exception as e:
    print(f"❌ Erro ao inicializar banco de dados: {e}")
    traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Iniciando aplicação Flask...")
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        traceback.print_exc()