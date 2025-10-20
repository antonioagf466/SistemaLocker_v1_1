from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from Core.sistema import SistemaLocker
from Models.cls_usuario import Administrador
from Core.helper import HelperMenus
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages and session

# Initialize the system
sistema = SistemaLocker()

@app.route('/')
def index():
    #if 'user_id' in session:
        #if session.get('is_admin'):
            #return redirect(url_for('admin_dashboard'))
        #return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('ID e senha são obrigatórios')
            return render_template('login.html')
            
        user = sistema.autenticar_usuario(user_id, password)
        if user:
            session['user_id'] = user.get_id()
            session['user_name'] = user.get_nome()
            session['is_admin'] = isinstance(user, Administrador)
            flash('Login realizado com sucesso!')
            if session['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session or session['is_admin']:
        return redirect(url_for('login'))
    
    user = sistema._SistemaLocker__usuarios.get(session['user_id'])
    return render_template('user_dashboard.html', user=user)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
    admin = sistema._SistemaLocker__usuarios.get(session['user_id'])
    return render_template('admin_dashboard.html', admin=admin)

@app.route('/user/action', methods=['POST'])
def user_action():
    if 'user_id' not in session:
        return jsonify({'html': 'Sessão expirada. Por favor, faça login novamente.'})
    
    action = request.form.get('action')
    user = sistema._SistemaLocker__usuarios.get(session['user_id'])
    result = ''
    
    if action == 'reservar_locker':
        result = HelperMenus.reservar_locker(user, sistema)
    elif action == 'liberar_locker':
        result = HelperMenus.liberar_locker(user, sistema)
    elif action == 'ver_locker':
        result = HelperMenus.ver_locker(user, sistema)
    elif action == 'ver_historico':
        result = HelperMenus.ver_historico(user, sistema)
    elif action == 'alterar_senha':
        result = HelperMenus.alterar_senha(user, sistema)
    
    return jsonify({'html': f'Resultado da ação {action}: {result}'})

@app.route('/admin/action', methods=['POST'])
def admin_action():
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'html': 'Acesso negado.'})
    
    action = request.form.get('action')
    admin = sistema._SistemaLocker__usuarios.get(session['user_id'])
    result = ''
    
    if action == 'adicionar_locker':
        result = HelperMenus.adicionar_locker(admin, sistema)
    elif action == 'colocar_manutencao':
        result = HelperMenus.colocar_manutencao(admin, sistema)
    elif action == 'remover_manutencao':
        result = HelperMenus.remover_manutencao(admin, sistema)
    elif action == 'listar_lockers':
        result = HelperMenus.listar_lockers(admin, sistema)
    elif action == 'listar_usuarios':
        result = HelperMenus.listar_usuarios(admin, sistema)
    elif action == 'forcar_liberacao':
        result = HelperMenus.forcar_liberacao(admin, sistema)
    elif action == 'remover_locker':
        result = HelperMenus.remover_locker(admin, sistema)
    
    return jsonify({'html': f'Resultado da ação {action}: {result}'})


if __name__ == "__main__":
    app.run(debug=True)