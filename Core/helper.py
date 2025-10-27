from Models.cls_usuario import *
from Models.cls_locker import *
from datetime import datetime, timedelta

#### Helper Functions - Static Methods Only ####
class HelperMenus:
    
    @staticmethod
    def get_formatted_time():
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    @staticmethod
    def _get_lockers_disponiveis(sistema):
        """Get all available lockers from the system"""
        lockers_disponiveis = {}
        
        # Read system data
        for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
            # If status is NOT 'Ocupado', the locker is available
            if locker_data.get('status') not in ['Ocupado', 'Manutencao']:
                lockers_disponiveis[locker_id] = {
                    'tamanho': locker_data['tamanho'],
                    'status': locker_data['status'],
                    'tempo_maximo': 1 if locker_data['tamanho'] == "Pequeno" else \
                                   2 if locker_data['tamanho'] == "Médio" else 4
                }
        
        return lockers_disponiveis
    
    @staticmethod
    def reservar_locker(usuario, sistema, form_data=None):
        """Reserve a locker for the user - Web version"""
        try:
            # Check if user already has a reserved locker
            usuario_id = usuario.get_id()
            for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
                if (locker_data.get('status') == 'Ocupado' and 
                    locker_data.get('reservado_por') == usuario_id):
                    return '<div class="error-message">Você já possui um locker reservado! (Locker {})</div>'.format(locker_id)

            # If no form data, show available lockers
            if form_data is None:
                # Get list of available lockers
                lockers_disponiveis = HelperMenus._get_lockers_disponiveis(sistema)
                
                if not lockers_disponiveis:
                    return '<div class="info-message">Não há lockers disponíveis no momento.</div>'
                
                html = '''
                    <h2>Reservar Locker</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tamanho</th>
                                <th>Tempo Máximo</th>
                                <th>Status</th>
                                <th>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for locker_id, locker_info in lockers_disponiveis.items():
                    html += f'''
                        <tr>
                            <td>{locker_id}</td>
                            <td>{locker_info['tamanho']}</td>
                            <td>{locker_info['tempo_maximo']} hora(s)</td>
                            <td>{locker_info['status']}</td>
                            <td>
                                <button onclick="submitReservaForm('{locker_id}')">
                                    Reservar
                                </button>
                            </td>
                        </tr>
                    '''
                
                html += '''
                        </tbody>
                    </table>
                    <script>
                        function submitReservaForm(lockerId) {
                            if(confirm("Deseja reservar este locker?")) {
                                $.post('/user/action', {
                                    action: 'reservar_locker',
                                    locker_id: lockerId,
                                    submit: true
                                }, function(response) {
                                    $('.result-content').html(response.html);
                                });
                            }
                        }
                    </script>
                '''
                return html

            # Process form submission
            if form_data.get('submit'):
                locker_id = form_data.get('locker_id')
                if not locker_id:
                    return '<div class="error-message">ID do locker não fornecido.</div>'
                
                locker_escolhido = sistema._SistemaLocker__lockers.get(locker_id)
                if not locker_escolhido:
                    return '<div class="error-message">Locker não encontrado.</div>'
                
                if locker_escolhido.get('status') in ['Ocupado', 'Manutencao']:
                    return '<div class="error-message">Este locker não está disponível.</div>'
                
                # Update locker data
                locker_escolhido['status'] = 'Ocupado'
                locker_escolhido['reservado_por'] = usuario.get_id()
                
                # Set time limit based on size
                data_atual = HelperMenus.get_formatted_time()
                horas_limite = 1 if locker_escolhido['tamanho'] == "Pequeno" else \
                            2 if locker_escolhido['tamanho'] == "Médio" else 4
                data_agora = datetime.now()
                locker_escolhido['data_reserva'] = data_atual
                locker_escolhido['tempo_limite'] = (data_agora + timedelta(hours=horas_limite)).strftime("%d-%m-%Y %H:%M:%S")
                
                # Update user data
                usuario.set_locker_reservado(locker_id)
                
                # Add to history
                historico = {
                    'locker_id': locker_id,
                    'data_reserva': data_atual,
                    'data_liberacao': None,
                    'tipo': locker_escolhido['tamanho'],
                    'status': 'Reservado'
                }
                usuario.adicionar_reserva(historico)
                
                # Save changes
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker reservado com sucesso!</h3>
                            <p>ID do Locker: {locker_id}</p>
                            <p>Tamanho: {locker_escolhido['tamanho']}</p>
                            <p>Tempo limite: {horas_limite} hora(s)</p>
                            <p>Data limite: {locker_escolhido['tempo_limite']}</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados. A reserva não foi concluída.</div>'
        
        except Exception as e:
            return f'<div class="error-message">Erro ao reservar locker: {str(e)}</div>'
        
    @staticmethod
    def liberar_locker(usuario, sistema, form_data=None):
        """Release a locker reserved by the user - Web version"""
        try:
            usuario_id = usuario.get_id()
            
            # Find the locker reserved by the user
            locker_reservado = None
            for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
                if (locker_data.get('status') == 'Ocupado' and 
                    locker_data.get('reservado_por') == usuario_id):
                    locker_reservado = locker_id
                    break
            
            # Check if user has any reserved locker
            if not locker_reservado:
                return '<div class="error-message">Você não possui nenhum locker reservado.</div>'
            
                # If no form data or not a submission, show confirmation form
            if form_data is None or not form_data.get('submit'):
                locker_data = sistema._SistemaLocker__lockers[locker_reservado]
                html = f'''
                    <h2>Liberar Locker</h2>
                    <div class="locker-info">
                        <p><strong>ID do Locker:</strong> {locker_reservado}</p>
                        <p><strong>Tamanho:</strong> {locker_data['tamanho']}</p>
                        <p><strong>Data de Reserva:</strong> {locker_data.get('data_reserva', 'N/A')}</p>
                        <p><strong>Tempo Limite:</strong> {locker_data.get('tempo_limite', 'N/A')}</p>
                    </div>
                    <div class="confirmation-buttons">
                        <button onclick="submitLiberarForm(\'{locker_reservado}\')" class="primary-button">
                            Confirmar Liberação
                        </button>
                        <button onclick="closeResult()" class="cancel-button">
                            Cancelar
                        </button>
                    </div>
                    <script>
                        function submitLiberarForm(lockerId) {{
                            if(confirm("Tem certeza que deseja liberar este locker?")) {{
                                $.post('/user/action', {{
                                    action: 'liberar_locker',
                                    locker_id: lockerId,
                                    submit: true
                                }}, function(response) {{
                                    $('.result-content').html(response.html);
                                    if(response.html.includes('success-message')) {{
                                        setTimeout(function() {{
                                            location.reload();
                                        }}, 2000);
                                    }}
                                }});
                            }}
                        }}
                    </script>
                '''
                return html

            # Process form submission
            locker_id = form_data.get('locker_id')
            if locker_id != locker_reservado:
                return '<div class="error-message">Locker inválido.</div>'
                
            locker_data = sistema._SistemaLocker__lockers[locker_id]
            
            # Release the locker
            locker_data['status'] = 'Disponivel'
            data_liberacao = HelperMenus.get_formatted_time()
            
            # Create history entry
            historico_liberacao = {
                'locker_id': locker_id,
                'data_reserva': locker_data.get('data_reserva', data_liberacao),
                'data_liberacao': data_liberacao,
                'tipo': locker_data['tamanho'],
                'status': 'Liberado'
            }
            
            # Update user data
            usuario.set_locker_reservado(None)
            usuario.adicionar_reserva(historico_liberacao)
            
            # Clean up locker data
            locker_data.pop('reservado_por', None)
            locker_data.pop('data_reserva', None)
            locker_data.pop('tempo_limite', None)
            
            # Save changes
            if sistema._salvar_dados():
                return f'''
                    <div class="success-message">
                        <h3>Locker liberado com sucesso!</h3>
                        <p>ID do Locker: {locker_id}</p>
                        <p>Tamanho: {locker_data['tamanho']}</p>
                        <p>Data de Liberação: {data_liberacao}</p>
                    </div>
                '''
            else:
                return '<div class="error-message">Erro ao salvar os dados. A liberação não foi concluída.</div>'
                
        except Exception as e:
            return f'<div class="error-message">Erro ao liberar locker: {str(e)}</div>'
        
    @staticmethod
    def ver_locker(usuario, sistema, form_data=None):
        """Check user's reserved locker - Web version"""
        try:
            usuario_id = usuario.get_id()
            
            # Find the locker reserved by the user
            locker_reservado = None
            for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
                if (locker_data.get('status') == 'Ocupado' and 
                    locker_data.get('reservado_por') == usuario_id):
                    locker_reservado = locker_id
                    break
            
            # Check if user has any reserved locker
            if not locker_reservado:
                return '<div class="error-message">Você não possui nenhum locker reservado.</div>'
            
            try:
                # Show current locker information
                locker_data = sistema._SistemaLocker__lockers[locker_reservado]
                tempo_limite = locker_data.get('tempo_limite', 'Não definido')
                
                return f'''
                    <div class="locker-info">
                        <h2>Seu Locker Atual</h2>
                        <p><strong>ID do Locker:</strong> {locker_reservado}</p>
                        <p><strong>Tamanho:</strong> {locker_data['tamanho']}</p>
                        <p><strong>Data de Reserva:</strong> {locker_data.get('data_reserva', 'N/A')}</p>
                        <p><strong>Tempo Limite:</strong> {tempo_limite}</p>
                        <p><strong>Status:</strong> {locker_data['status']}</p>
                    </div>
                '''
            
            except Exception as e:
                return f'<div class="error-message">Erro ao visualizar locker: {str(e)}</div>'
                
        except Exception as e:
            return f'<div class="error-message">Erro ao buscar locker: {str(e)}</div>'
    @staticmethod
    def ver_historico(usuario, sistema, form_data=None):
        """View user's reservation history - Web version"""
        try:
            historico_reservas = usuario.get_historico_reservas()
            
            if not historico_reservas:
                return '<div class="info-message">Você não possui histórico de reservas.</div>'
            
            html = f'''
                <h2>Histórico de Reservas - {usuario.get_nome()}</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Locker ID</th>
                            <th>Tipo</th>
                            <th>Data Reserva</th>
                            <th>Data Liberação</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            for reserva in historico_reservas:
                locker_id = reserva.get('locker_id', 'N/A')
                tipo = reserva.get('tipo', 'N/A')
                data_reserva = reserva.get('data_reserva', 'N/A')
                data_liberacao = reserva.get('data_liberacao') or 'Em uso'
                status = reserva.get('status', 'N/A')
                
                html += f'''
                    <tr>
                        <td>{locker_id}</td>
                        <td>{tipo}</td>
                        <td>{data_reserva}</td>
                        <td>{data_liberacao}</td>
                        <td>{status}</td>
                    </tr>
                '''
            
            html += f'''
                    </tbody>
                </table>
                <p class="total-reservas">Total de reservas: {len(historico_reservas)}</p>
            '''
            return html
            
        except Exception as e:
            return f'<div class="error-message">Erro ao visualizar histórico: {str(e)}</div>'
    @staticmethod
    def alterar_senha(usuario, sistema, form_data=None):
        """Change user password - Web version"""
        try:
            if form_data is None:
                return '''
                    <h2>Alterar Senha</h2>
                    <form id="changePasswordForm" onsubmit="submitPasswordForm(event)">
                        <div class="form-group">
                            <label>Nova Senha:</label>
                            <input type="password" name="nova_senha" required>
                        </div>
                        <div class="form-group">
                            <label>Confirmar Nova Senha:</label>
                            <input type="password" name="confirmar_senha" required>
                        </div>
                        <div class="form-buttons">
                            <button type="submit">Alterar Senha</button>
                            <button type="button" class="cancel-button" onclick="closeResult()">Cancelar</button>
                        </div>
                    </form>
                    <script>
                        function submitPasswordForm(event) {
                            event.preventDefault();
                            const form = event.target;
                            const nova_senha = form.elements['nova_senha'].value;
                            const confirmar_senha = form.elements['confirmar_senha'].value;
                            
                            if (nova_senha !== confirmar_senha) {
                                alert('As senhas não coincidem!');
                                return;
                            }
                            
                            $.post('/user/action', {
                                action: 'alterar_senha',
                                nova_senha: nova_senha,
                                submit: true
                            }, function(response) {
                                $('.result-content').html(response.html);
                            });
                        }
                    </script>
                '''
            
            # Process form submission
            if form_data.get('submit'):
                nova_senha = form_data.get('nova_senha')
                if not nova_senha:
                    return '<div class="error-message">A nova senha não pode estar vazia.</div>'
                
                # Update the user's password
                usuario._Usuario__senha = nova_senha
                
                # Save changes to JSON file
                if sistema._salvar_dados():
                    return '''
                        <div class="success-message">
                            <h3>Senha alterada com sucesso!</h3>
                            <p>Sua senha foi atualizada.</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados. A senha não foi alterada.</div>'
                    
        except Exception as e:
            return f'<div class="error-message">Erro ao alterar senha: {str(e)}</div>'
    @staticmethod
    def adicionar_locker(admin, sistema, form_data=None):
        """Add a new locker - Web version"""
        try:
            # If no form data, return the form HTML
            if form_data is None:
                return '''
                    <h2>Adicionar Novo Locker</h2>
                    <form id="addLockerForm" onsubmit="submitLockerForm(event)">
                        <div class="form-group">
                            <label>Tamanho do Locker:</label><br>
                            <select name="tamanho" required>
                                <option value="Pequeno">Pequeno (1 hora máxima)</option>
                                <option value="Medio">Médio (2 horas máximas)</option>
                                <option value="Grande">Grande (4 horas máximas)</option>
                            </select>
                        </div>
                        <button type="submit">Adicionar Locker</button>
                    </form>
                    <script>
                        function submitLockerForm(event) {
                            event.preventDefault();
                            const formData = new FormData(event.target);
                            $.post('/admin/action', {
                                action: 'adicionar_locker',
                                tamanho: formData.get('tamanho'),
                                submit: true
                            }, function(response) {
                                $('.result-content').html(response.html);
                            });
                        }
                    </script>
                '''

            # Process form submission
            if form_data.get('submit'):
                # Get existing locker IDs and find the first available ID
                existing_ids = list(sistema._SistemaLocker__lockers.keys())
                if existing_ids:
                    numeric_ids = [int(lid) for lid in existing_ids if lid.isdigit()]
                    numeric_ids.sort()
                    
                    novo_id = "101"
                    if numeric_ids:
                        for i in range(101, max(numeric_ids) + 2):
                            if i not in numeric_ids:
                                novo_id = str(i)
                                break
                else:
                    novo_id = "101"

                # Create the new locker
                tamanho = form_data.get('tamanho')
                novo_locker = {
                    'tamanho': tamanho,
                    'status': 'Disponivel'
                }
                
                # Add to system
                sistema._SistemaLocker__lockers[novo_id] = novo_locker
                
                # Save changes to JSON file
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker adicionado com sucesso!</h3>
                            <p>ID do Locker: {novo_id}</p>
                            <p>Tamanho: {tamanho}</p>
                            <p>Status: Disponível</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados. Locker não foi adicionado.</div>'
    
        except Exception as e:
            return f'<div class="error-message">Erro ao adicionar locker: {str(e)}</div>'
    @staticmethod
    def colocar_manutencao(admin, sistema, form_data=None):
        try:
            if form_data is None:
                # Get all lockers for display
                all_lockers = sistema._SistemaLocker__lockers
                
                # Create HTML for table of lockers
                html = '''
                    <h2>Colocar Locker em Manutenção</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tamanho</th>
                                <th>Status</th>
                                <th>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for locker_id, locker_data in all_lockers.items():
                    status = locker_data.get('status', 'N/A')
                    if status not in ['Ocupado', 'Manutencao']:
                        html += f'''
                            <tr>
                                <td>{locker_id}</td>
                                <td>{locker_data.get('tamanho', 'N/A')}</td>
                                <td>{status}</td>
                                <td>
                                    <button onclick="submitMaintenanceForm('{locker_id}')">
                                        Colocar em Manutenção
                                    </button>
                                </td>
                            </tr>
                        '''
                
                html += '''
                        </tbody>
                    </table>
                    <script>
                        function submitMaintenanceForm(lockerId) {
                            if(confirm("Deseja colocar este locker em manutenção?")) {
                                $.post('/admin/action', {
                                    action: 'colocar_manutencao',
                                    locker_id: lockerId,
                                    submit: true
                                }, function(response) {
                                    $('.result-content').html(response.html);
                                });
                            }
                        }
                    </script>
                '''
                return html

            # Process form submission
            if form_data.get('submit'):
                locker_id = form_data.get('locker_id')
                locker_data = sistema._SistemaLocker__lockers.get(locker_id)
                
                if not locker_data:
                    return '<div class="error-message">Locker não encontrado.</div>'
                
                if locker_data.get('status') in ['Ocupado', 'Manutencao']:
                    return '<div class="error-message">Este locker não pode ser colocado em manutenção.</div>'
                
                # Put locker under maintenance
                locker_data['status'] = 'Manutencao'
                locker_data['data_manutencao'] = HelperMenus.get_formatted_time()
                
                # Save changes
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker colocado em manutenção com sucesso!</h3>
                            <p>ID do Locker: {locker_id}</p>
                            <p>Tamanho: {locker_data['tamanho']}</p>
                            <p>Data: {locker_data['data_manutencao']}</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados.</div>'
                    
        except Exception as e:
            return f'<div class="error-message">Erro: {str(e)}</div>'
    
    @staticmethod
    def remover_manutencao(admin, sistema, form_data=None):
        try:
            if form_data is None:
                # Get lockers under maintenance
                lockers_manutencao = {lid: data for lid, data in sistema._SistemaLocker__lockers.items() 
                                    if data.get('status') == 'Manutencao'}
                
                if not lockers_manutencao:
                    return '<div class="info-message">Não há lockers em manutenção no momento.</div>'
                
                html = '''
                    <h2>Remover Locker da Manutenção</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tamanho</th>
                                <th>Data Manutenção</th>
                                <th>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for locker_id, locker_data in lockers_manutencao.items():
                    html += f'''
                        <tr>
                            <td>{locker_id}</td>
                            <td>{locker_data.get('tamanho', 'N/A')}</td>
                            <td>{locker_data.get('data_manutencao', 'N/A')}</td>
                            <td>
                                <button onclick="submitRemoveMaintenanceForm('{locker_id}')">
                                    Remover da Manutenção
                                </button>
                            </td>
                        </tr>
                    '''
                
                html += '''
                        </tbody>
                    </table>
                    <script>
                        function submitRemoveMaintenanceForm(lockerId) {
                            if(confirm("Deseja remover este locker da manutenção?")) {
                                $.post('/admin/action', {
                                    action: 'remover_manutencao',
                                    locker_id: lockerId,
                                    submit: true
                                }, function(response) {
                                    $('.result-content').html(response.html);
                                });
                            }
                        }
                    </script>
                '''
                return html

            # Process form submission
            if form_data.get('submit'):
                locker_id = form_data.get('locker_id')
                locker_data = sistema._SistemaLocker__lockers.get(locker_id)
                
                if not locker_data or locker_data.get('status') != 'Manutencao':
                    return '<div class="error-message">Locker não encontrado ou não está em manutenção.</div>'
                
                # Remove from maintenance
                locker_data['status'] = 'Disponivel'
                locker_data.pop('data_manutencao', None)
                
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker removido da manutenção com sucesso!</h3>
                            <p>ID do Locker: {locker_id}</p>
                            <p>Tamanho: {locker_data['tamanho']}</p>
                            <p>Novo Status: Disponível</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados.</div>'
                    
        except Exception as e:
            return f'<div class="error-message">Erro: {str(e)}</div>'
    @staticmethod
    def listar_lockers(admin, sistema, form_data=None):
        try:
            # Always return HTML table since this is just a display function
            html = '''
                <h2>Lista de Todos os Lockers</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tamanho</th>
                            <th>Status</th>
                            <th>ID Usuário</th>
                            <th>Nome Usuário</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
                tamanho = locker_data.get('tamanho', 'N/A')
                status = locker_data.get('status', 'N/A')
                
                if status == 'Ocupado':
                    user_id = locker_data.get('reservado_por', 'N/A')
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    user_name = user.get_nome() if user else 'N/A'
                else:
                    user_id = 'N/A'
                    user_name = 'N/A'
                
                html += f'''
                    <tr>
                        <td>{locker_id}</td>
                        <td>{tamanho}</td>
                        <td>{status}</td>
                        <td>{user_id}</td>
                        <td>{user_name}</td>
                    </tr>
                '''
            
            html += '''
                    </tbody>
                </table>
            '''
            return html
            
        except Exception as e:
            return f'<div class="error-message">Erro ao listar lockers: {str(e)}</div>'
        
    @staticmethod
    def listar_usuarios(admin, sistema, form_data=None):
        try:
            html = '''
                <h2>Lista de Todos os Usuários</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Tipo</th>
                            <th>Locker ID</th>
                            <th>Tamanho Locker</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            for user_id, user in sistema._SistemaLocker__usuarios.items():
                nome = user.get_nome()
                tipo = "Admin" if isinstance(user, Administrador) else "Usuário"
                
                # Get locker info if user has one reserved
                locker_id = 'N/A'
                locker_tamanho = 'N/A'
                
                for lid, locker_data in sistema._SistemaLocker__lockers.items():
                    if (locker_data.get('status') == 'Ocupado' and 
                        locker_data.get('reservado_por') == user_id):
                        locker_id = lid
                        locker_tamanho = locker_data.get('tamanho', 'N/A')
                        break
                
                html += f'''
                    <tr>
                        <td>{user_id}</td>
                        <td>{nome}</td>
                        <td>{tipo}</td>
                        <td>{locker_id}</td>
                        <td>{locker_tamanho}</td>
                    </tr>
                '''
            
            html += '''
                    </tbody>
                </table>
            '''
            return html
            
        except Exception as e:
            return f'<div class="error-message">Erro ao listar usuários: {str(e)}</div>'

    @staticmethod
    def forcar_liberacao(admin, sistema, form_data=None):
        try:
            if form_data is None:
                # Get all occupied lockers
                lockers_ocupados = {lid: data for lid, data in sistema._SistemaLocker__lockers.items() 
                                if data.get('status') == 'Ocupado'}
                
                if not lockers_ocupados:
                    return '<div class="info-message">Não há lockers ocupados no momento.</div>'
                
                html = '''
                    <h2>Forçar Liberação de Locker</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tamanho</th>
                                <th>ID Usuário</th>
                                <th>Nome Usuário</th>
                                <th>Data Reserva</th>
                                <th>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for locker_id, locker_data in lockers_ocupados.items():
                    user_id = locker_data.get('reservado_por', 'N/A')
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    user_name = user.get_nome() if user else 'N/A'
                    
                    html += f'''
                        <tr>
                            <td>{locker_id}</td>
                            <td>{locker_data.get('tamanho', 'N/A')}</td>
                            <td>{user_id}</td>
                            <td>{user_name}</td>
                            <td>{locker_data.get('data_reserva', 'N/A')}</td>
                            <td>
                                <button onclick="submitForceReleaseForm('{locker_id}')">
                                    Forçar Liberação
                                </button>
                            </td>
                        </tr>
                    '''
                
                html += '''
                        </tbody>
                    </table>
                    <script>
                        function submitForceReleaseForm(lockerId) {
                            if(confirm("Tem certeza que deseja forçar a liberação deste locker?")) {
                                $.post('/admin/action', {
                                    action: 'forcar_liberacao',
                                    locker_id: lockerId,
                                    submit: true
                                }, function(response) {
                                    $('.result-content').html(response.html);
                                });
                            }
                        }
                    </script>
                '''
                return html

            # Process form submission
            if form_data.get('submit'):
                locker_id = form_data.get('locker_id')
                locker_data = sistema._SistemaLocker__lockers.get(locker_id)
                
                if not locker_data or locker_data.get('status') != 'Ocupado':
                    return '<div class="error-message">Locker não encontrado ou não está ocupado.</div>'
                
                # Force release the locker
                user_id = locker_data.get('reservado_por')
                user = sistema._SistemaLocker__usuarios.get(user_id)
                data_liberacao = HelperMenus.get_formatted_time()
                
                # Update locker status
                locker_data['status'] = 'Disponivel'
                
                # Update user data if exists
                if user:
                    user.set_locker_reservado(None)
                    historico_liberacao = {
                        'locker_id': locker_id,
                        'data_reserva': locker_data.get('data_reserva', data_liberacao),
                        'data_liberacao': data_liberacao,
                        'tipo': locker_data['tamanho'],
                        'status': 'Liberado (Forçado)'
                    }
                    user.adicionar_reserva(historico_liberacao)
                
                # Clean up locker data
                locker_data.pop('reservado_por', None)
                locker_data.pop('data_reserva', None)
                locker_data.pop('tempo_limite', None)
                
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker liberado forçadamente com sucesso!</h3>
                            <p>ID do Locker: {locker_id}</p>
                            <p>Tamanho: {locker_data['tamanho']}</p>
                            <p>Usuário anterior: {user.get_nome() if user else 'N/A'}</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados.</div>'
                    
        except Exception as e:
            return f'<div class="error-message">Erro ao forçar liberação: {str(e)}</div>'
    @staticmethod
    def remover_locker(admin, sistema, form_data=None):
        try:
            if form_data is None:
                # Get all lockers
                all_lockers = sistema._SistemaLocker__lockers
                if not all_lockers:
                    return '<div class="info-message">Não há lockers no sistema.</div>'
                
                html = '''
                    <h2>Remover Locker</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tamanho</th>
                                <th>Status</th>
                                <th>ID Usuário</th>
                                <th>Nome Usuário</th>
                                <th>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for locker_id, locker_data in all_lockers.items():
                    tamanho = locker_data.get('tamanho', 'N/A')
                    status = locker_data.get('status', 'N/A')
                    
                    if status == 'Ocupado':
                        user_id = locker_data.get('reservado_por', 'N/A')
                        user = sistema._SistemaLocker__usuarios.get(user_id)
                        user_name = user.get_nome() if user else 'N/A'
                    else:
                        user_id = 'N/A'
                        user_name = 'N/A'
                    
                    # Only show remove button for non-occupied lockers
                    button_html = '''
                        <button onclick="submitRemoveLockerForm('{}')">
                            Remover Locker
                        </button>
                    '''.format(locker_id) if status != 'Ocupado' else 'Locker Ocupado'
                    
                    html += f'''
                        <tr>
                            <td>{locker_id}</td>
                            <td>{tamanho}</td>
                            <td>{status}</td>
                            <td>{user_id}</td>
                            <td>{user_name}</td>
                            <td>{button_html}</td>
                        </tr>
                    '''
                
                html += '''
                        </tbody>
                    </table>
                    <script>
                        function submitRemoveLockerForm(lockerId) {
                            if(confirm("Tem certeza que deseja remover este locker?")) {
                                $.post('/admin/action', {
                                    action: 'remover_locker',
                                    locker_id: lockerId,
                                    submit: true
                                }, function(response) {
                                    $('.result-content').html(response.html);
                                });
                            }
                        }
                    </script>
                '''
                return html

            # Process form submission
            if form_data.get('submit'):
                locker_id = form_data.get('locker_id')
                locker_data = sistema._SistemaLocker__lockers.get(locker_id)
                
                if not locker_data:
                    return '<div class="error-message">Locker não encontrado.</div>'
                
                if locker_data.get('status') == 'Ocupado':
                    user_id = locker_data.get('reservado_por')
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    return f'''
                        <div class="error-message">
                            <p>Este locker está ocupado por {user.get_nome() if user else 'usuário desconhecido'}!</p>
                            <p>Você precisa forçar a liberação do locker antes de removê-lo.</p>
                        </div>
                    '''
                
                # Remove the locker
                tamanho = locker_data.get('tamanho', 'N/A')
                status = locker_data.get('status', 'N/A')
                del sistema._SistemaLocker__lockers[locker_id]
                
                if sistema._salvar_dados():
                    return f'''
                        <div class="success-message">
                            <h3>Locker removido com sucesso!</h3>
                            <p>ID: {locker_id}</p>
                            <p>Tamanho: {tamanho}</p>
                            <p>Status anterior: {status}</p>
                        </div>
                    '''
                else:
                    return '<div class="error-message">Erro ao salvar os dados. O locker não foi removido.</div>'
                    
        except Exception as e:
            return f'<div class="error-message">Erro ao remover locker: {str(e)}</div>'