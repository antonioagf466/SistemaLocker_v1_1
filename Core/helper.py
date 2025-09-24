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
    def reservar_locker(usuario, sistema):
        """Reserve a locker for the user"""
        # Check if user already has a reserved locker
        usuario_id = usuario.get_id()
        for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
            if (locker_data.get('status') == 'Ocupado' and 
                locker_data.get('reservado_por') == usuario_id):
                print(f"\nVocê já possui um locker reservado! (Locker {locker_id})")
                return False

        # Get list of available lockers
        lockers_disponiveis = HelperMenus._get_lockers_disponiveis(sistema)
        
        print("\nLockers Disponíveis:")
        print("-" * 50)
        print("ID  | Tamanho | Tempo Máximo | Status")
        print("-" * 50)
        
        for locker_id, locker_info in lockers_disponiveis.items():
            print(f"{locker_id} | {locker_info['tamanho']:8} | {locker_info['tempo_maximo']} hora(s)    | {locker_info['status']}")
        
        if not lockers_disponiveis:
            print("\nNão há lockers disponíveis no momento.")
            return False
        
        # Request user choice
        while True:
            try:
                escolha = input("\nDigite o ID do locker desejado (ou 0 para cancelar): ").strip()
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
                
                if escolha not in [str(lid) for lid in lockers_disponiveis]:
                    print("ID de locker inválido. Escolha um dos lockers disponíveis.")
                    continue
                
                # Reserve the locker
                locker_escolhido = sistema._SistemaLocker__lockers[escolha]
                
                # Update locker data with user ID instead of name
                locker_escolhido['status'] = 'Ocupado'
                locker_escolhido['reservado_por'] = usuario.get_id()  # Store ID instead of name
                
                # Set time limit based on size
                data_atual = HelperMenus.get_formatted_time()
                horas_limite = 1 if locker_escolhido['tamanho'] == "Pequeno" else \
                              2 if locker_escolhido['tamanho'] == "Médio" else 4
                data_agora = datetime.now()
                locker_escolhido['data_reserva'] = data_atual
                locker_escolhido['tempo_limite'] = (data_agora + timedelta(hours=horas_limite)).strftime("%d-%m-%Y %H:%M:%S")
                
                # Update user data
                usuario.set_locker_reservado(escolha)
                
                # Add to history
                historico = {
                    'locker_id': escolha,
                    'data_reserva': data_atual,
                    'data_liberacao': None,
                    'tipo': locker_escolhido['tamanho'],
                    'status': 'Reservado'
                }
                usuario.adicionar_reserva(historico)
                
                # Save changes to JSON file
                sistema._salvar_dados()
                
                print(f"\nLocker {escolha} reservado com sucesso!")
                print(f"Tempo limite: {horas_limite} hora(s)")
                return True
                
            except ValueError:
                print("Entrada inválida. Digite apenas o número do locker.")
            except Exception as e:
                print(f"Erro ao reservar locker: {str(e)}")
                return False
    
    @staticmethod
    def liberar_locker(usuario, sistema):
        """Release a locker reserved by the user"""
        usuario_id = usuario.get_id()
        
        # Find the locker reserved by the user
        locker_reservado = None
        for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
            if (locker_data.get('status') == 'Ocupado' and 
                locker_data.get('reservado_por') == usuario_id):  # Check by ID
                locker_reservado = locker_id
                break
        
        # Check if user has any reserved locker
        if not locker_reservado:
            print(f"\nUsuário {usuario.get_nome()} não possui nenhum locker reservado.")  # Show name
            return False
        
        try:
            # Show current locker information
            locker_data = sistema._SistemaLocker__lockers[locker_reservado]
            print(f"\nLocker reservado para {usuario.get_nome()}:")  # Show name
            print(f"ID: {locker_reservado}")
            print(f"Tamanho: {locker_data['tamanho']}")
            
            # Confirmation
            confirmacao = input(f"\nDeseja liberar o locker {locker_reservado}? (s/n): ").strip().lower()
            if confirmacao not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada.")
                return False
            
            # Release the locker
            locker_data['status'] = 'Disponivel'
            locker_data.pop('reservado_por', None)
            locker_data.pop('data_reserva', None)
            locker_data.pop('tempo_limite', None)
            
            # Update user data
            usuario.set_locker_reservado(None)
            
            # Add release entry to user history
            data_liberacao = HelperMenus.get_formatted_time()
            
            # Create a new history entry for the release
            historico_liberacao = {
                'locker_id': locker_reservado,
                'data_reserva': locker_data.get('data_reserva', data_liberacao),
                'data_liberacao': data_liberacao,
                'tipo': locker_data['tamanho'],
                'status': 'Liberado'
            }
            usuario.adicionar_reserva(historico_liberacao)
            
            # Save changes to JSON file
            sistema._salvar_dados()
            
            print(f"\nLocker {locker_reservado} foi liberado.")
            return True
            
        except Exception as e:
            print(f"Erro ao liberar locker: {str(e)}")
            return False
    @staticmethod
    def ver_locker(usuario, sistema):
        """Check user's reserved locker"""
        usuario_id = usuario.get_id()
        
        # Find the locker reserved by the user
        locker_reservado = None
        for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
            if (locker_data.get('status') == 'Ocupado' and 
                locker_data.get('reservado_por') == usuario_id):  # Check by ID
                locker_reservado = locker_id
                break
        
        # Check if user has any reserved locker
        if not locker_reservado:
            print(f"\nUsuário {usuario.get_nome()} não tem um locker reservado")  # Show name
            return False
        
        try:
            # Show current locker information
            locker_data = sistema._SistemaLocker__lockers[locker_reservado]
            tempo_limite = locker_data.get('tempo_limite', 'Não definido')
            
            print(f"\nLocker reservado para {usuario.get_nome()}:")  # Show name
            print(f"ID do Locker: {locker_reservado}")
            print(f"Tamanho: {locker_data['tamanho']}")
            print(f"Tempo limite: {tempo_limite}")
            return True
        
        except Exception as e:
            print(f"Erro ao visualizar locker: {str(e)}")
            return False
    @staticmethod  
    def ver_historico(usuario, sistema):   
        try:  
            historico_reservas = usuario.get_historico_reservas()  
            
            if not historico_reservas:  
                print("\nVocê não possui histórico de reservas.")  
                return False  
            
            print(f"\nHistórico de Reservas - {usuario.get_nome()}")  
            print("=" * 80)  
            print(f"{'Locker ID':<10} {'Tipo':<8} {'Data Reserva':<20} {'Data Liberação':<20} {'Status':<10}")  
            print("-" * 80)  
            
            for reserva in historico_reservas:  
                locker_id = reserva.get('locker_id', 'N/A')  
                tipo = reserva.get('tipo', 'N/A')  
                data_reserva = reserva.get('data_reserva', 'N/A')  
                data_liberacao = reserva.get('data_liberacao') or 'Em uso'  
                status = reserva.get('status', 'N/A')  
                
                print(f"{locker_id:<10} {tipo:<8} {data_reserva:<20} {data_liberacao:<20} {status:<10}")  
            
            print("-" * 80)  
            print(f"Total de reservas: {len(historico_reservas)}")  
            return True  
            
        except Exception as e:  
            print(f"Erro ao visualizar histórico: {str(e)}")  
            return False
    @staticmethod
    def alterar_senha(usuario, sistema):
        try:
            nova_senha = input("Digite a nova senha: ").strip()
            if not nova_senha:
                print("Senha não pode estar vazia.")
                return False
            
            confirmar_senha = input("Confirme a nova senha: ").strip()
            if nova_senha != confirmar_senha:
                print("As senhas não coincidem.")
                return False
            
            # Update the user's password
            usuario._Usuario__senha = nova_senha
            
            # Save changes to JSON file
            sistema._salvar_dados()
            
            print("Senha alterada com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao alterar senha: {str(e)}")
            return False
    @staticmethod
    def adicionar_locker(admin, sistema):
        try:
            print("\n=== ADICIONAR NOVO LOCKER ===")
            
            # Get existing locker IDs and find the first available ID
            existing_ids = list(sistema._SistemaLocker__lockers.keys())
            if existing_ids:
                # Convert existing IDs to integers
                numeric_ids = [int(lid) for lid in existing_ids if lid.isdigit()]
                numeric_ids.sort()  # Sort IDs in ascending order
                
                # Find first gap in sequence starting from 101
                novo_id = "101"  # Default start
                if numeric_ids:
                    for i in range(101, max(numeric_ids) + 2):
                        if i not in numeric_ids:
                            novo_id = str(i)
                            break
            else:
                novo_id = "101"  # First locker
            
            print(f"ID do novo locker será: {novo_id}")
            
            # Ask for locker size
            print("\nEscolha o tamanho do locker:")
            print("1. Pequeno (1 hora máxima)")
            print("2. Médio (2 horas máximas)")
            print("3. Grande (4 horas máximas)")
            
            while True:
                escolha_tamanho = input("\nDigite sua escolha (1-3) ou 0 para cancelar: ").strip()
                
                if escolha_tamanho == "0":
                    print("Operação cancelada.")
                    return False
                elif escolha_tamanho == "1":
                    tamanho = "Pequeno"
                    break
                elif escolha_tamanho == "2":
                    tamanho = "Medio"
                    break
                elif escolha_tamanho == "3":
                    tamanho = "Grande"
                    break
                else:
                    print("Opção inválida. Digite 1, 2, 3 ou 0.")
            
            # Confirmation
            print(f"\nConfirmar criação do locker:")
            print(f"ID: {novo_id}")
            print(f"Tamanho: {tamanho}")
            
            confirmacao = input("\nDeseja criar este locker? (s/n): ").strip().lower()
            if confirmacao not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada.")
                return False
            
            # Create the new locker
            novo_locker = {
                'tamanho': tamanho,
                'status': 'Disponivel'
            }
            
            # Add to system
            sistema._SistemaLocker__lockers[novo_id] = novo_locker
            
            # Save changes to JSON file
            if sistema._salvar_dados():
                print(f"\nLocker {novo_id} ({tamanho}) adicionado com sucesso!")
                return True
            else:
                print("\nErro ao salvar os dados. Locker não foi adicionado.")
                return False
        
        except Exception as e:
            print(f"Erro ao adicionar locker: {str(e)}")
            return False
    @staticmethod
    def colocar_manutencao(admin, sistema):
        try:
            print("\n=== COLOCAR LOCKER EM MANUTENÇÃO ===")
        
            # Show ALL lockers and their status
            all_lockers = sistema._SistemaLocker__lockers
            if not all_lockers:
                print("\nNão há lockers no sistema.")
                return False
            
            print("\nTodos os Lockers no Sistema:")
            print("-" * 70)
            print(f"{'ID':<5} | {'Tamanho':<8} | {'Status':<15} | {'Reservado Por':<15}")
            print("-" * 70)
            
            for locker_id, locker_data in all_lockers.items():
                status = locker_data.get('status', 'N/A')
                tamanho = locker_data.get('tamanho', 'N/A')
                reservado_por = locker_data.get('reservado_por', 'N/A')
                
                print(f"{locker_id:<5} | {tamanho:<8} | {status:<15} | {reservado_por:<15}")
                
                print("-" * 70)
            
            # Ask admin to choose a locker
            while True:
                escolha = input("\nDigite o ID do locker para colocar em manutenção (ou 0 para cancelar): ").strip()
            
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
            
                if escolha not in all_lockers:
                    print("ID de locker inválido. Escolha um dos lockers listados.")
                    continue
            
            # Check if locker can be put under maintenance
                locker_data = all_lockers[escolha]
                current_status = locker_data.get('status')
            
                if current_status == 'Ocupado':
                    print("Você não pode adicionar este locker em manutenção no momento - está ocupado.")
                    continue
                elif current_status == 'Manutencao':
                    print("Você não pode adicionar este locker em manutenção no momento - já está em manutenção.")
                    continue
            
                # Confirmation
                print(f"\nConfirmar colocação em manutenção:")
                print(f"ID: {escolha}")
                print(f"Tamanho: {locker_data['tamanho']}")
                print(f"Status atual: {current_status}")
            
                confirmacao = input("\nDeseja colocar este locker em manutenção? (s/n): ").strip().lower()
                if confirmacao not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return False
            
                # Put locker under maintenance
                locker_data['status'] = 'Manutencao'
                locker_data['data_manutencao'] = HelperMenus.get_formatted_time()
            
                # Save changes to JSON file
                if sistema._salvar_dados():
                    print(f"\nLocker {escolha} colocado em manutenção com sucesso!")
                    return True
                else:
                    print("\nErro ao salvar os dados. Locker não foi colocado em manutenção.")
                    return False
        
        except Exception as e:
            print(f"Erro ao colocar locker em manutenção: {str(e)}")
            return False
    
    @staticmethod
    def remover_manutencao(admin, sistema):
        try:
            print("\n=== REMOVER LOCKER DA MANUTENÇÃO ===")
            
            # Get all lockers under maintenance
            all_lockers = sistema._SistemaLocker__lockers
            lockers_manutencao = {}
            
            for locker_id, locker_data in all_lockers.items():
                if locker_data.get('status') == 'Manutencao':
                    lockers_manutencao[locker_id] = locker_data
            
            if not lockers_manutencao:
                print("\nNão há lockers em manutenção no momento.")
                return False
            
            print("\nLockers em Manutenção:")
            print("-" * 70)
            print(f"{'ID':<5} | {'Tamanho':<8} | {'Status':<15} | {'Data Manutenção':<20}")
            print("-" * 70)
            
            for locker_id, locker_data in lockers_manutencao.items():
                tamanho = locker_data.get('tamanho', 'N/A')
                status = locker_data.get('status', 'N/A')
                data_manutencao = locker_data.get('data_manutencao', 'N/A')
                
                print(f"{locker_id:<5} | {tamanho:<8} | {status:<15} | {data_manutencao:<20}")
                
                print("-" * 70)
            
            # Ask admin to choose a locker to remove from maintenance
            while True:
                escolha = input("\nDigite o ID do locker para remover da manutenção (ou 0 para cancelar): ").strip()
                
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
                
                if escolha not in lockers_manutencao:
                    print("ID de locker inválido. Escolha um dos lockers em manutenção.")
                    continue
                
                # Confirmation
                locker_data = lockers_manutencao[escolha]
                print(f"\nConfirmar remoção da manutenção:")
                print(f"ID: {escolha}")
                print(f"Tamanho: {locker_data['tamanho']}")
                print(f"Status atual: {locker_data['status']}")
                print(f"Data da manutenção: {locker_data.get('data_manutencao', 'N/A')}")
                
                confirmacao = input("\nDeseja remover este locker da manutenção? (s/n): ").strip().lower()
                if confirmacao not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return False
                
                # Remove from maintenance - set back to available
                locker_data['status'] = 'Disponivel'
                locker_data.pop('data_manutencao', None)  # Remove maintenance date
                
                # Save changes to JSON file
                if sistema._salvar_dados():
                    print(f"\nLocker {escolha} removido da manutenção com sucesso! Status: Disponível")
                    return True
                else:
                    print("\nErro ao salvar os dados. Locker não foi removido da manutenção.")
                    return False
        
        except Exception as e:
            print(f"Erro ao remover locker da manutenção: {str(e)}")
            return False
    @staticmethod
    def listar_lockers(admin, sistema):
        try:
            print("\n=== Todos os lockers ===")
            
            # Get all lockers
            all_lockers = sistema._SistemaLocker__lockers
            print("\nTodos lockers:")
            print("-" * 100)
            print(f"{'ID':<5} | {'Tamanho':<8} | {'Status':<15} | {'ID Usuario':<12} | {'Nome Usuario':<20}")
            print("-" * 100)
            
            for locker_id, locker_data in all_lockers.items():
                tamanho = locker_data.get('tamanho', 'N/A')
                status = locker_data.get('status', 'N/A')
                
                # Get user info if locker is occupied
                if status == 'Ocupado':
                    user_id = locker_data.get('reservado_por', 'N/A')
                    # Get user name from sistema
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    user_name = user.get_nome() if user else 'N/A'
                else:
                    user_id = 'N/A'
                    user_name = 'N/A'
                
                print(f"{locker_id:<5} | {tamanho:<8} | {status:<15} | {user_id:<12} | {user_name:<20}")
            
            print("-" * 100)
            return True
        except Exception as e:
            print(f"Erro ao mostrar os lockers: {str(e)}")
            return False
    @staticmethod
    def listar_usuarios(admin, sistema):
        try:
            print("\n=== Todos os Usuários ===")
            print("-" * 100)
            print(f"{'ID':<10} | {'Nome':<20} | {'Tipo':<10} | {'Locker ID':<10} | {'Tamanho':<10}")
            print("-" * 100)
            
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
                
                print(f"{user_id:<10} | {nome:<20} | {tipo:<10} | {locker_id:<10} | {locker_tamanho:<10}")
            
            print("-" * 100)
            return True
        except Exception as e:
            print(f"Erro ao mostrar os usuários: {str(e)}")
            return False
    @staticmethod
    def forcar_liberacao(admin, sistema):
        try:
            print("\n=== FORÇAR LIBERAÇÃO DE LOCKER ===")
            
            # Get all occupied lockers
            lockers_ocupados = {}
            for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
                if locker_data.get('status') == 'Ocupado':
                    lockers_ocupados[locker_id] = locker_data
            
            if not lockers_ocupados:
                print("\nNão há lockers ocupados no momento.")
                return False
            
            # Display occupied lockers
            print("\nLockers Ocupados:")
            print("-" * 100)
            print(f"{'ID':<5} | {'Tamanho':<8} | {'Usuario ID':<12} | {'Nome Usuario':<20} | {'Data Reserva':<20}")
            print("-" * 100)
            
            for locker_id, locker_data in lockers_ocupados.items():
                tamanho = locker_data.get('tamanho', 'N/A')
                user_id = locker_data.get('reservado_por', 'N/A')
                data_reserva = locker_data.get('data_reserva', 'N/A')
                
                # Get user name
                user = sistema._SistemaLocker__usuarios.get(user_id)
                user_name = user.get_nome() if user else 'N/A'
                
                print(f"{locker_id:<5} | {tamanho:<8} | {user_id:<12} | {user_name:<20} | {data_reserva:<20}")
            
            print("-" * 100)
            
            # Ask for locker ID to force release
            while True:
                escolha = input("\nDigite o ID do locker para forçar liberação (ou 0 para cancelar): ").strip()
                
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
                
                if escolha not in lockers_ocupados:
                    print("ID de locker inválido. Escolha um dos lockers ocupados.")
                    continue
                
                # Confirmation
                locker_data = lockers_ocupados[escolha]
                user_id = locker_data.get('reservado_por')
                user = sistema._SistemaLocker__usuarios.get(user_id)
                
                print(f"\nConfirmar liberação forçada:")
                print(f"ID do Locker: {escolha}")
                print(f"Tamanho: {locker_data['tamanho']}")
                print(f"Usuário: {user.get_nome() if user else 'N/A'}")
                
                confirmacao = input("\nDeseja forçar a liberação deste locker? (s/n): ").strip().lower()
                if confirmacao not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return False
                
                # Force release the locker
                locker_data['status'] = 'Disponivel'
                data_liberacao = HelperMenus.get_formatted_time()
                
                # Update user data if user still exists
                if user:
                    # Update user's locker reservation status
                    user.set_locker_reservado(None)
                    
                    # Add release entry to user history
                    historico_liberacao = {
                        'locker_id': escolha,
                        'data_reserva': locker_data.get('data_reserva', data_liberacao),
                        'data_liberacao': data_liberacao,
                        'tipo': locker_data['tamanho'],
                        'status': 'Liberado (Forcado)'
                    }
                    user.adicionar_reserva(historico_liberacao)
                
                # Clean up locker data
                locker_data.pop('reservado_por', None)
                locker_data.pop('data_reserva', None)
                locker_data.pop('tempo_limite', None)
                
                # Save changes to JSON file
                if sistema._salvar_dados():
                    print(f"\nLocker {escolha} foi liberado forçadamente com sucesso!")
                    return True
                else:
                    print("\nErro ao salvar os dados. A liberação forçada não foi concluída.")
                    return False
                
        except Exception as e:
            print(f"Erro ao forçar liberação do locker: {str(e)}")
            return False
    @staticmethod
    def remover_locker(admin, sistema):
        try:
            print("\n=== REMOVER LOCKER ===")
            
            # Get all lockers
            all_lockers = sistema._SistemaLocker__lockers
            if not all_lockers:
                print("\nNão há lockers no sistema.")
                return False
            
            # Display all lockers with their status and user info
            print("\nLockers Disponíveis:")
            print("-" * 100)
            print(f"{'ID':<5} | {'Tamanho':<8} | {'Status':<15} | {'ID Usuario':<12} | {'Nome Usuario':<20}")
            print("-" * 100)
            
            for locker_id, locker_data in all_lockers.items():
                tamanho = locker_data.get('tamanho', 'N/A')
                status = locker_data.get('status', 'N/A')
                
                # Get user info if locker is occupied
                if status == 'Ocupado':
                    user_id = locker_data.get('reservado_por', 'N/A')
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    user_name = user.get_nome() if user else 'N/A'
                else:
                    user_id = 'N/A'
                    user_name = 'N/A'
                
                print(f"{locker_id:<5} | {tamanho:<8} | {status:<15} | {user_id:<12} | {user_name:<20}")
            
            print("-" * 100)
            
            # Ask for locker ID to remove
            while True:
                escolha = input("\nDigite o ID do locker para remover (ou 0 para cancelar): ").strip()
                
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
                
                if escolha not in all_lockers:
                    print("ID de locker inválido. Escolha um dos lockers listados.")
                    continue
                
                # Check if locker is occupied
                locker_data = all_lockers[escolha]
                if locker_data.get('status') == 'Ocupado':
                    user_id = locker_data.get('reservado_por')
                    user = sistema._SistemaLocker__usuarios.get(user_id)
                    print(f"\nAtenção: Este locker está ocupado por {user.get_nome() if user else 'usuário desconhecido'}!")
                    print("Você precisa forçar a liberação do locker antes de removê-lo.")
                    return False
                
                # Confirmation
                print(f"\nConfirmar remoção do locker:")
                print(f"ID: {escolha}")
                print(f"Tamanho: {locker_data['tamanho']}")
                print(f"Status atual: {locker_data['status']}")
                
                confirmacao = input("\nDeseja remover este locker? (s/n): ").strip().lower()
                if confirmacao not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return False
                
                # Remove the locker
                del sistema._SistemaLocker__lockers[escolha]
                
                # Save changes to JSON file
                if sistema._salvar_dados():
                    print(f"\nLocker {escolha} foi removido com sucesso!")
                    return True
                else:
                    print("\nErro ao salvar os dados. O locker não foi removido.")
                    return False
                
        except Exception as e:
            print(f"Erro ao remover locker: {str(e)}")
            return False
        
    #Historico do sistema
    #Perguntar para o sor na aula.......