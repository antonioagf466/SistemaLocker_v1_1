from Models.cls_usuario import *
from Models.cls_locker import *
######################### Helper Apenas #################################
class HelperMenus:
    
    ######## Instancia EXCLUSIVAMENTE para acesso facil do sistema #############
    
    def __init__(self, sistema):
        self.__sistema = sistema
    
    # Este método retorna o sistema para acesso interno
    def _get_sistema(self):
        return self.__sistema
############################################################################



    def _get_lockers_disponiveis(self):
        sistema = self._get_sistema()
        lockers_disponiveis = {}
        
        # Ler dados do sistema
        for locker_id, locker_data in sistema._SistemaLocker__lockers.items():
            # Se o status NÃO for 'Ocupado', o locker está disponível
            if locker_data.get('status') != 'Ocupado':
                lockers_disponiveis[locker_id] = {
                    'tamanho': locker_data['tamanho'],
                    'status': locker_data['status'],
                    'tempo_maximo': 1 if locker_data['tamanho'] == "Pequeno" else \
                                  2 if locker_data['tamanho'] == "Médio" else 4
                }
        
        return lockers_disponiveis
    def reservar_locker(self, usuario):
        # Verificar se o usuário já possui um locker reservado
        if usuario.get_locker_reservado():
            print("\nVocê já possui um locker reservado!")
            return False

        # Obter lista de lockers disponíveis
        lockers_disponiveis = self._get_lockers_disponiveis()
        sistema = self._get_sistema()
        
        print("\nLockers Disponíveis:")
        print("-" * 50)
        print("ID  | Tamanho | Tempo Máximo | Status")
        print("-" * 50)
        
        for locker_id, locker_info in lockers_disponiveis.items():
            print(f"{locker_id} | {locker_info['tamanho']:8} | {locker_info['tempo_maximo']} hora(s)    | {locker_info['status']}")
        
        if not lockers_disponiveis:
            print("\nNão há lockers disponíveis no momento.")
            return False
        
        # Solicitar escolha do usuário
        while True:
            try:
                escolha = input("\nDigite o ID do locker desejado (ou 0 para cancelar): ").strip()
                if escolha == "0":
                    print("Operação cancelada.")
                    return False
                
                if escolha not in [str(lid) for lid in lockers_disponiveis]:
                    print("ID de locker inválido. Escolha um dos lockers disponíveis.")
                    continue
                
                # Reservar o locker
                locker_escolhido = sistema._SistemaLocker__lockers[escolha]
                
                # Atualizar dados do locker
                locker_escolhido['status'] = 'Ocupado'
                locker_escolhido['reservado_por'] = usuario.get_id()
                
                # Definir tempo limite baseado no tamanho
                from datetime import datetime, timedelta
                data_atual = datetime.now()
                horas_limite = 1 if locker_escolhido['tamanho'] == "Pequeno" else \
                             2 if locker_escolhido['tamanho'] == "Médio" else 4
                
                locker_escolhido['data_reserva'] = data_atual.isoformat()
                locker_escolhido['tempo_limite'] = (data_atual + timedelta(hours=horas_limite)).isoformat()
                
                # Atualizar dados do usuário
                usuario.set_locker_reservado(escolha)
                
                # Adicionar ao histórico
                historico = {
                    'locker_id': escolha,
                    'data_reserva': data_atual.isoformat(),
                    'data_liberacao': None,
                    'tipo': locker_escolhido['tamanho'],
                    'status': 'Reservado'
                }
                usuario.adicionar_reserva(historico)
                
                # Salvar alterações no arquivo JSON
                sistema._salvar_dados()
                
                print(f"\nLocker {escolha} reservado com sucesso!")
                print(f"Tempo limite: {horas_limite} hora(s)")
                return True
                
            except ValueError:
                print("Entrada inválida. Digite apenas o número do locker.")
            except Exception as e:
                print(f"Erro ao reservar locker: {str(e)}")
                return False