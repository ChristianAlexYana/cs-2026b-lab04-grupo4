"""Adaptadores de integraciones externas (ADR-001, ADR-003)."""
from abc import ABC, abstractmethod
from .dominio import Cita
from .puertos import Notificador
from .externos import WhatsAppSDK, ReniecSDK

# 1. Adaptador para WhatsApp (Completando el que ya tenías del Lab 05)
class WhatsAppAdapter(Notificador):
    def __init__(self, sdk=WhatsAppSDK()):
        self.sdk = sdk
        
    def programar_recordatorio(self, cita: Cita) -> None:
        # Traduce la llamada de tu dominio al SDK externo
        res = self.sdk.enviar_mensaje(cita.celular, f"Cita {cita.id} reservada")
        if not res.get("ok"):
            raise ValueError("Fallo al programar recordatorio en WhatsApp")

# 2. Adaptador para el DNI (El que agregamos para el Lab 07)
class ValidadorIdentidad(ABC):
    @abstractmethod
    def validar_dni(self, dni: str) -> bool: pass

class DniAdapter(ValidadorIdentidad):
    def __init__(self, sdk=ReniecSDK()):
        self.sdk = sdk
        
    def validar_dni(self, dni: str) -> bool:
        codigo, datos = self.sdk.consultar(dni)
        return codigo == 200 and datos.get("valido", False)