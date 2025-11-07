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
    
    try:
        # Handle form submissions
        if request.form.get('submit'):
            result = getattr(HelperMenus, action)(user, sistema, request.form)
        # Handle initial display
        else:
            result = getattr(HelperMenus, action)(user, sistema)
            
        return jsonify({'html': result})
        
    except Exception as e:
        print(f"Error in user_action: {str(e)}")  # Add debug print
        return jsonify({'html': f'<div class="error-message">Erro: {str(e)}</div>'})

@app.route('/admin/action', methods=['POST'])
def admin_action():
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'html': 'Acesso negado.'})
    
    action = request.form.get('action')
    admin = sistema._SistemaLocker__usuarios.get(session['user_id'])
    
    try:
        # Verify if the action exists in HelperMenus
        if not hasattr(HelperMenus, action):
            return jsonify({'html': f'<div class="error-message">Ação "{action}" não implementada.</div>'})
        
        # For initial load or direct actions
        if request.form.get('initial') == 'true':
            result = getattr(HelperMenus, action)(admin, sistema)
            return jsonify({'html': result})
        
        # For form submissions
        if request.form.get('submit') == 'true':
            result = getattr(HelperMenus, action)(admin, sistema, request.form)
            return jsonify({'html': result})
            
        return jsonify({'html': '<div class="error-message">Requisição inválida.</div>'})
    except Exception as e:
        print(f"Error in admin_action: {str(e)}")  # Add debug print
        return jsonify({'html': f'<div class="error-message">Erro: {str(e)}</div>'})

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)