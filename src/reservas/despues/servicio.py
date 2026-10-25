"""Versión «después» del flujo reservar_cita: Strategy, Adapter, State, Observer y Decorator."""
from src.reservas.adaptadores import DniAdapter, WhatsAppAdapter
from src.reservas.antes.servicio import Cita
from src.reservas.estados import Borrador, Cancelada, CitaContexto, Reservada
from src.reservas.eventos import ConReintentos, NotificadorWhatsApp, PublicadorEventos, Suscriptor
from src.reservas.externos import ReniecSDK, WhatsAppSDK
from src.reservas.politicas import FabricaPoliticas


class _ReservadaMensajePropio(Reservada):
    def reservar(self, cita):
        raise ValueError("La cita ya está reservada")


class _CanceladaMensajePropio(Cancelada):
    def reservar(self, cita):
        raise ValueError("La cita está cancelada")


ESTADOS = {
    "BORRADOR": Borrador,
    "RESERVADA": _ReservadaMensajePropio,
    "CANCELADA": _CanceladaMensajePropio,
}


class ContextoEstado(CitaContexto):
    """State: parte del estado actual de la cita; no modifica la cita hasta confirmar."""

    def __init__(self, nombre_estado: str) -> None:
        super().__init__()
        if nombre_estado not in ESTADOS:
            raise ValueError("Estado no válido")
        self.estado_actual = ESTADOS[nombre_estado]()


class RegistroEventos(Suscriptor):
    def __init__(self, eventos: list) -> None:
        self._eventos = eventos

    def actualizar(self, evento: str, cita) -> None:
        if evento == "CITA_RESERVADA":
            self._eventos.append(f"whatsapp: {cita.celular}: Cita {cita.id} reservada")


class ServicioReservasDespues:
    def __init__(self, validador=None, notificador=None, fabrica=None) -> None:
        self.validador = validador or DniAdapter(ReniecSDK())
        self.fabrica = fabrica or FabricaPoliticas()
        self.eventos = []
        self.cupos_db = {"Medicina General": True, "Cardiologia": False}  # Simulación BD
        notificador = notificador or ConReintentos(WhatsAppAdapter(WhatsAppSDK()))
        self.publicador = PublicadorEventos()
        self.publicador.suscribir(NotificadorWhatsApp(notificador))
        self.publicador.suscribir(RegistroEventos(self.eventos))

    def reservar_cita(self, cita: Cita, politica_alternativos: str = "PRONTO") -> str:
        contexto = ContextoEstado(cita.estado)
        contexto.reservar()
        if not self.validador.validar_dni(cita.paciente_dni):
            raise ValueError("DNI inválido")
        self._asegurar_cupo(cita.especialidad, politica_alternativos)

        cita.cupo_ocupado = True
        cita.estado = contexto.estado_actual.nombre
        try:
            self.publicador.publicar("CITA_RESERVADA", cita)
        except TimeoutError:
            raise ValueError("Error de red al notificar")
        return cita.estado

    def _asegurar_cupo(self, especialidad: str, nombre_politica: str) -> None:
        if self.cupos_db.get(especialidad, False):
            return
        politica = self.fabrica.crear(nombre_politica)
        if not politica.buscar_cupo(especialidad, self.cupos_db):
            raise ValueError("No hay cupos alternativos")