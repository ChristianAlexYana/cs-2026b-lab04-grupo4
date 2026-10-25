"""Observer (E4): el servicio publica eventos y los suscriptores reaccionan."""
from abc import ABC, abstractmethod

from .puertos import Notificador


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, cita) -> None: ...


class PublicadorEventos:
    def __init__(self) -> None:
        self._suscriptores: list[Suscriptor] = []

    def suscribir(self, suscriptor: Suscriptor) -> None:
        self._suscriptores.append(suscriptor)

    def publicar(self, evento: str, cita) -> None:
        for suscriptor in self._suscriptores:
            suscriptor.actualizar(evento, cita)


class NotificadorWhatsApp(Suscriptor):
    """Suscriptor 1: programa el recordatorio por WhatsApp."""

    def __init__(self, notificador: Notificador) -> None:
        self._notificador = notificador

    def actualizar(self, evento: str, cita) -> None:
        if evento == "CITA_RESERVADA":
            self._notificador.programar_recordatorio(cita)


class SuscriptorAuditoria(Suscriptor):
    """Suscriptor 2: deja registro de cada evento."""

    def __init__(self) -> None:
        self.registro: list[str] = []

    def actualizar(self, evento: str, cita) -> None:
        self.registro.append(f"{evento}: cita {cita.id}")

class ConReintentos(Notificador):
    """Decorator: reintenta el envío solo ante TimeoutError."""

    def __init__(self, notificador: Notificador, max_intentos: int = 3) -> None:
        self._notificador = notificador
        self._max_intentos = max_intentos

    def programar_recordatorio(self, cita) -> None:
        for intento in range(1, self._max_intentos + 1):
            try:
                self._notificador.programar_recordatorio(cita)
                return
            except TimeoutError:
                if intento == self._max_intentos:
                    raise
