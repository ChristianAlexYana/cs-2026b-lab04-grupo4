"""Puertos (interfaces) como clases abstractas (ADR-001, ADR-005)."""
from abc import ABC, abstractmethod
from uuid import UUID

from .dominio import Cita, Cupo


class RepositorioCupos(ABC):
    @abstractmethod
    def buscar_por_id(self, id: UUID) -> Cupo: ...

    @abstractmethod
    def buscar_disponibles(self, especialidad: str, centro_id: UUID) -> list[Cupo]: ...

    @abstractmethod
    def guardar(self, cupo: Cupo) -> None: ...


class RepositorioCitas(ABC):
    @abstractmethod
    def buscar_por_id(self, id: UUID) -> Cita: ...

    @abstractmethod
    def guardar(self, cita: Cita) -> None: ...


class Notificador(ABC):
    @abstractmethod
    def programar_recordatorio(self, cita: Cita) -> None: ...
