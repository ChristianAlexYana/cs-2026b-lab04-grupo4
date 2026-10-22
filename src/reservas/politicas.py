from abc import ABC, abstractmethod

class PoliticaAsignacionCupo(ABC):
    @abstractmethod
    def buscar_cupo(self, especialidad: str, cupos_db: dict) -> bool: pass

class PoliticaMasProntoDisponible(PoliticaAsignacionCupo):
    def buscar_cupo(self, especialidad, cupos_db):
        return True # Simula encontrar el más pronto

class PoliticaMismoMedico(PoliticaAsignacionCupo):
    def buscar_cupo(self, especialidad, cupos_db):
        return False # Simula no encontrar el mismo médico

class FabricaPoliticas:
    def __init__(self):
        self._creadores = {
            "PRONTO": PoliticaMasProntoDisponible,
            "MISMO_MEDICO": PoliticaMismoMedico
        }
    def crear(self, nombre: str) -> PoliticaAsignacionCupo:
        if nombre not in self._creadores:
            raise ValueError(f"Política no soportada: {nombre}")
        return self._creadores[nombre]()