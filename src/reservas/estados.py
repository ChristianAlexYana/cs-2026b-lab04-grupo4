class EstadoDeCita:
    nombre = "?"
    def reservar(self, cita):
        raise ValueError(f"No se puede reservar una cita en estado {self.nombre}")
    def cancelar(self, cita):
        raise ValueError(f"No se puede cancelar una cita en estado {self.nombre}")

class Borrador(EstadoDeCita):
    nombre = "BORRADOR"
    def reservar(self, cita):
        cita.cambiar_estado(Reservada())

class Reservada(EstadoDeCita):
    nombre = "RESERVADA"
    def cancelar(self, cita):
        cita.cambiar_estado(Cancelada())

class Cancelada(EstadoDeCita):
    nombre = "CANCELADA"

class CitaContexto:
    def __init__(self):
        self.estado_actual = Borrador()
    def cambiar_estado(self, nuevo_estado):
        self.estado_actual = nuevo_estado
    def reservar(self):
        self.estado_actual.reservar(self)
    def cancelar(self):
        self.estado_actual.cancelar(self)