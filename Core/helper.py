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
            if locker_data.get('status') != 'Ocupado':
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
                locker_data.get('reservado_por') == usuario_id):
                locker_reservado = locker_id
                break
        
        # Check if user has any reserved locker
        if not locker_reservado:
            print("\nVocê não possui nenhum locker reservado.")
            return False
        
        try:
            # Show current locker information
            locker_data = sistema._SistemaLocker__lockers[locker_reservado]
            print(f"\nSeu locker reservado:")
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
            
            print(f"\nLocker {locker_reservado} está liberado.")
            return True
            
        except Exception as e:
            print(f"Erro ao liberar locker: {str(e)}")
            return False
    @staticmethod
    def ver_locker(usuario, sistema):
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
            print("\nVocê não tem um locker reservado")
            return False
        
        try:
        # Show current locker information
            locker_data = sistema._SistemaLocker__lockers[locker_reservado]
            tempo_limite = locker_data.get('tempo_limite', 'Não definido')
            
            print(f"\nSeu locker reservado:")
            print(f"ID do Locker: {locker_reservado}")
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