"""Adaptadores de integraciones externas (ADR-001, ADR-003)."""
from .dominio import Cita
from .puertos import Notificador


class WhatsAppAdapter(Notificador):
    def programar_recordatorio(self, cita: Cita) -> None:
        raise NotImplementedError
