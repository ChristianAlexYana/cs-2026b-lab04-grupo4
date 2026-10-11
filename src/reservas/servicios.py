"""Servicios de aplicación (esqueleto)."""
from uuid import UUID

from .dominio import Cita, Cupo
from .puertos import Notificador, RepositorioCitas, RepositorioCupos


class ServicioDisponibilidad:
    def __init__(self, repositorio_cupos: RepositorioCupos) -> None:
        self._repositorio_cupos = repositorio_cupos

    def buscar_alternativos(self, cupo: Cupo) -> list[Cupo]:
        raise NotImplementedError


class ServicioReservas:
    def __init__(
        self,
        repositorio_citas: RepositorioCitas,
        repositorio_cupos: RepositorioCupos,
        notificador: Notificador,
        servicio_disponibilidad: ServicioDisponibilidad,
    ) -> None:
        self._repositorio_citas = repositorio_citas
        self._repositorio_cupos = repositorio_cupos
        self._notificador = notificador
        self._servicio_disponibilidad = servicio_disponibilidad

    def reservar_cita(self, paciente_id: UUID, cupo_id: UUID) -> Cita:
        raise NotImplementedError

    def cancelar_cita(self, cita_id: UUID, motivo: str) -> None:
        raise NotImplementedError
