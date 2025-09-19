class Locker:
    def __init__(self, locker_id, tamanho):
        self.__id = locker_id
        self.__tamanho = tamanho
        self.__status = "Disponível"
        self.__reservado_por = None
        self.__data_reserva = None
        self.__tempo_limite = None

    def set_status(self, status):
        self.__status = status

    def set_reservado_por(self, usuario):
        self.__reservado_por = usuario

    def set_data_reserva(self, data):
        self.__data_reserva = data

    def set_tempo_limite(self, tempo):
        self.__tempo_limite = tempo


class LockerPequeno(Locker):
    def get_tempo_maximo(self):
        return 1

    def reservar(self, usuario_id):
        print("Regra: tempo máximo de reserva = 1 hora")



class LockerMedio(Locker):
    def get_tempo_maximo(self):
        return 2

    def reservar(self, usuario_id):
        print("Regra: tempo máximo de reserva = 2 horas")



class LockerGrande(Locker):
    def get_tempo_maximo(self):
        return 4

    def reservar(self, usuario_id):
        print("Regra: tempo máximo de reserva = 4 horas")

