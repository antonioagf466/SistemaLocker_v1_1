class Usuario:
    def __init__(self, nome, usuario_id, senha):
        self.__nome = nome
        self.__id = usuario_id
        self.__senha = senha
        self.__locker_reservado = None
        self.__historico_reservas = []

    def set_locker_reservado(self, locker_reservado):
        self.__locker_reservado = locker_reservado

    def adicionar_reserva(self, reserva):
        self.__historico_reservas.append(reserva)

    def verificar_senha(self, senha_digitada):
        return self.__senha == senha_digitada

    def get_nome(self):
        return self.__nome
    
    def get_senha(self):
        return self.__senha
    
    def get_id(self):
        return self.__id
    
    def get_locker_reservado(self):
        return self.__locker_reservado
    
    def get_historico_reservas(self):
        return self.__historico_reservas

class Administrador(Usuario):
    def __init__(self, nome, usuario_id, senha):
        super().__init__(nome, usuario_id, senha)
        self.__is_admin = True
        


