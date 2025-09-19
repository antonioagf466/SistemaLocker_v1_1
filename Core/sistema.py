
from datetime import datetime
from Models.cls_locker import *
from Models.cls_usuario import *
import json

class SistemaLocker:
    def __init__(self, arquivo_dados="Data/sistema_dados.json"):
        self.__usuarios = {}
        self.__lockers = {}
        self.__arquivo_dados = arquivo_dados
        #self.__inicializar_dados_padrao()
        self.carregar_dados()  
    
    # def __inicializar_dados_padrao(self):
    #     admin = Administrador("Ivonei", "admin01", "1234")
    #     user = Usuario("Carlos", "user01", "abcd")

    #     self.__usuarios["admin01"] = admin
    #     self.__usuarios["user01"] = user

    #     self.__lockers[101] = LockerPequeno(101, "Pequeno")
    #     self.__lockers[102] = LockerMedio(102, "Médio")
    #     self.__lockers[103] = LockerGrande(103, "Grande")
    def carregar_dados(self):
        try:
            with open(self.__arquivo_dados, 'r') as arquivo:
                dados = json.load(arquivo)
                usuarios_data = dados.get('usuarios', {})
                
                # Convert JSON data to Usuario/Administrador objects
                for user_id, user_data in usuarios_data.items():
                    if user_data['tipo'] == 'admin':
                        usuario = Administrador(user_data['nome'], user_id, user_data['senha'])
                    else:
                        usuario = Usuario(user_data['nome'], user_id, user_data['senha'])
                    self.__usuarios[user_id] = usuario
                
                self.__lockers = dados.get('lockers', {})
        except FileNotFoundError:
            print(f"Arquivo {self.__arquivo_dados} não encontrado. Usando dados padrão.")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar {self.__arquivo_dados}. Usando dados padrão.")
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}. Usando dados padrão.")
        
    def autenticar_usuario(self, nome_usuario, senha):
        if not nome_usuario.strip() or not senha.strip():
            print("Nome e senha são obrigatórios.")
            return None

        # Procura o usuário pelo nome ao invés do ID
        for usuario in self.__usuarios.values():
            if usuario.get_nome().lower() == nome_usuario.lower():  # Case-insensitive comparison
                if usuario.verificar_senha(senha):
                    print("Login realizado com sucesso!")
                    return usuario
                else:
                    print("Senha incorreta.")
                    return None
        
        print("Usuário não encontrado.")
        return None

    def gerar_novo_id_usuario(self, is_admin=False):
        prefix = "admin" if is_admin else "user"
        existing_ids = [uid for uid in self.__usuarios.keys() if uid.startswith(prefix)]
        if not existing_ids:
            return f"{prefix}01"
        
        # Get the highest number and increment
        highest = max([int(uid[len(prefix):]) for uid in existing_ids])
        return f"{prefix}{(highest + 1):02d}"  # Ensures 2-digit format

    def adicionar_usuario(self, nome, senha, is_admin=False):
        if not nome.strip() or not senha.strip():
            print("Nome e senha são obrigatórios.")
            return None

        novo_id = self.gerar_novo_id_usuario(is_admin)
        if is_admin:
            novo_usuario = Administrador(nome, novo_id, senha)
        else:
            novo_usuario = Usuario(nome, novo_id, senha)

        self.__usuarios[novo_id] = novo_usuario
        
        # Save updated data to JSON file
        try:
            dados = {
            'usuarios': {
                uid: {
                'nome': u.get_nome(),
                'senha': u.get_senha(),
                'tipo': 'admin' if isinstance(u, Administrador) else 'user'
                } for uid, u in self.__usuarios.items()
            },
            'lockers': self.__lockers
            }
            with open(self.__arquivo_dados, 'w') as arquivo:
                json.dump(dados, arquivo, indent=4)
                print(f"Usuário {'Administrador' if is_admin else 'Padrão'} '{nome}' adicionado com ID: {novo_id}")
                return novo_usuario
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            return None
            
    def _salvar_dados(self):
        try:
            dados = {
                'usuarios': {
                    uid: {
                        'nome': u.get_nome(),
                        'senha': u.get_senha(),
                        'tipo': 'admin' if isinstance(u, Administrador) else 'user',
                        'locker_reservado': u.get_locker_reservado(),
                        'historico_reservas': u.get_historico_reservas()
                    } for uid, u in self.__usuarios.items()
                },
                'lockers': self.__lockers
            }
            with open(self.__arquivo_dados, 'w') as arquivo:
                json.dump(dados, arquivo, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            return False
