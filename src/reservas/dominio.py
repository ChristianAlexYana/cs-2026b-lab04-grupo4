"""Entidades y enumeración del dominio (clases.puml)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class EstadoCita(Enum):
    RESERVADA = "RESERVADA"
    CONFIRMADA = "CONFIRMADA"
    ATENDIDA = "ATENDIDA"
    NO_ASISTIO = "NO_ASISTIO"
    CANCELADA = "CANCELADA"


@dataclass
class Paciente:
    id: UUID
    nombre: str
    celular: str


@dataclass
class CentroSalud:
    id: UUID
    nombre: str
    distrito: str


@dataclass
class Medico:
    id: UUID
    nombre: str
    especialidad: str


@dataclass
class Cupo:
    id: UUID
    fecha_hora: datetime
    ocupado: bool = False

    def esta_disponible(self) -> bool:
        return not self.ocupado

    def ocupar(self) -> None:
        if self.ocupado:
            raise ValueError("cupo ocupado")
        self.ocupado = True

    def liberar(self) -> None:
        self.ocupado = False


@dataclass
class Cita:
    id: UUID
    fecha_registro: datetime
    estado: EstadoCita
    motivo_cancelacion: str | None = None

    @staticmethod
    def crear(paciente: Paciente, cupo: Cupo) -> Cita:
        # Nota: la cita no guarda referencia a paciente ni a cupo (el diagrama los
        # relaciona por asociación, pero aquí no hay atributo que los almacene).
        return Cita(id=uuid4(), fecha_registro=datetime.now(), estado=EstadoCita.RESERVADA)

    def confirmar(self) -> None:
        if self.estado is not EstadoCita.RESERVADA:
            raise ValueError("solo una cita RESERVADA se puede confirmar")
        self.estado = EstadoCita.CONFIRMADA

    def atender(self) -> None:
        if self.estado is not EstadoCita.CONFIRMADA:
            raise ValueError("solo una cita CONFIRMADA se puede atender")
        self.estado = EstadoCita.ATENDIDA

    def marcar_no_asistio(self) -> None:
        if not self.esta_activa():
            raise ValueError("solo una cita activa puede marcarse como no asistió")
        self.estado = EstadoCita.NO_ASISTIO

    def cancelar(self, motivo: str) -> None:
        if not self.esta_activa():
            raise ValueError("solo una cita activa se puede cancelar")
        self.estado = EstadoCita.CANCELADA
        self.motivo_cancelacion = motivo

    def esta_activa(self) -> bool:
        return self.estado in (EstadoCita.RESERVADA, EstadoCita.CONFIRMADA)
