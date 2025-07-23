from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import database # Importe seu módulo de banco de dados
import datetime
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui_para_producao' # MUDE ISSO EM PRODUÇÃO!
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30) # Exemplo: sessão dura 30 minutos

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
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('dashboard'))
            else:
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
        average_risk_score = database.get_average_risk_score_value()
        treated_items_last_30_days = database.get_treated_items_last_30_days_count()
        risk_level_distribution = database.get_risk_level_distribution_data()
        identified_items_trend = database.get_identified_items_trend_data()

        return render_template(
            'dashboard.html',
            total_executives=total_executives,
            critical_pending_items=critical_pending_items,
            average_risk_score=average_risk_score,
            treated_items_last_30_days=treated_items_last_30_days,
            risk_level_distribution=risk_level_distribution,
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
                             average_risk_score=0.0,
                             treated_items_last_30_days=0,
                             risk_level_distribution={},
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
        risk_score = float(request.form['risk_score'])
        risk_level = request.form['risk_level']

        if database.add_executive(name, email, role, department, risk_score, risk_level):
            flash('Executivo adicionado com sucesso!', 'success')
            return redirect(url_for('executives'))
        else:
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
        risk_score = float(request.form['risk_score'])
        risk_level = request.form['risk_level']

        if database.update_executive(executive_id, name, email, role, department, risk_score, risk_level):
            flash('Executivo atualizado com sucesso!', 'success')
            return redirect(url_for('executives'))
        else:
            flash('Erro: Já existe outro executivo com este e-mail.', 'danger')
            return render_template('add_edit_executive.html', executive=executive, active_page='executives') # Renderiza com os dados originais
    return render_template('add_edit_executive.html', executive=executive, active_page='executives')

@app.route('/delete_executive/<int:executive_id>', methods=['POST'])
@login_required
def delete_executive(executive_id):
    database.delete_executive(executive_id)
    flash('Executivo excluído com sucesso!', 'success')
    return redirect(url_for('executives'))


@app.route('/items')
@login_required
def items():
    all_executives = database.get_all_executives() # Para o filtro de executivos
    all_items = database.get_all_items()
    return render_template('items.html', items=all_items, executives=all_executives, active_page='items')

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

        database.add_item(executive_id, title, description, item_type, severity, status, identified_date)
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
    if request.method == 'POST':
        executive_id = request.form['executive_id']
        title = request.form['title']
        description = request.form.get('description')
        item_type = request.form['type']
        severity = request.form['severity']
        status = request.form['status']
        identified_date = request.form['identified_date']

        database.update_item(item_id, executive_id, title, description, item_type, severity, status, identified_date)
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('items'))
    return render_template('add_edit_item.html', item=item, executives=executives_list, active_page='items')


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    database.delete_item(item_id)
    flash('Item excluído com sucesso!', 'success')
    return redirect(url_for('items'))

@app.route('/mark_item_treated/<int:item_id>', methods=['POST'])
@login_required
def mark_item_treated(item_id):
    item = database.get_item_by_id(item_id)
    if item:
        database.update_item(item_id, item['executive_id'], item['title'], item['description'], item['type'], item['severity'], 'TRATADO', item['identified_date'])
        flash('Item marcado como TRATADO!', 'success')
    else:
        flash('Item não encontrado.', 'danger')
    return redirect(url_for('items'))

@app.route('/mark_item_ignored/<int:item_id>', methods=['POST'])
@login_required
def mark_item_ignored(item_id):
    item = database.get_item_by_id(item_id)
    if item:
        database.update_item(item_id, item['executive_id'], item['title'], item['description'], item['type'], item['severity'], 'IGNORADO', item['identified_date'])
        flash('Item marcado como IGNORADO!', 'info')
    else:
        flash('Item não encontrado.', 'danger')
    return redirect(url_for('items'))


@app.route('/reports')
@login_required
def reports():
    try:
        return render_template('reports.html', active_page='reports')
    except Exception as e:
        print(f"Erro na rota reports: {e}")
        return render_template('reports.html', active_page='reports')

@app.route('/settings')
@login_required
def settings():
    try:
        return render_template('settings.html', active_page='settings')
    except Exception as e:
        print(f"Erro na rota settings: {e}")
        return render_template('settings.html', active_page='settings')

# --- Inicialização do banco de dados ---
try:
    with app.app_context():
        database.init_db()
        print("✅ Banco de dados inicializado com sucesso")
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