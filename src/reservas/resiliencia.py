"""Tácticas de disponibilidad para el servicio de DNI (Lab 08, iteración 2, QA-02).

Son Decorators del puerto `ValidadorIdentidad` (ADR-006): se apilan sobre `DniAdapter`
sin modificarlo ni tocar el servicio de reservas. Orden recomendado (de fuera hacia dentro):

    ValidadorConDegradacion(ValidadorConCircuitBreaker(ValidadorConReintentos(DniAdapter(sdk))))

`ConReintentos` (eventos.py) está tipado para `Notificador`, por eso aquí se aplica la
misma idea (reintentar solo ante TimeoutError) al puerto del DNI.
"""
from __future__ import annotations

import time
from typing import Callable

from .puertos import ValidadorIdentidad


class CircuitoAbierto(Exception):
    """El breaker está abierto: no se llamó al servicio externo."""


class CircuitBreaker:
    """CERRADO -> (umbral de fallos) -> ABIERTO -> (espera) -> SEMIABIERTO -> CERRADO/ABIERTO.

    Solo cuenta TimeoutError como fallo del proveedor. El reloj se inyecta para poder
    probarlo y simularlo sin esperar de verdad.
    """

    CERRADO, ABIERTO, SEMIABIERTO = "CERRADO", "ABIERTO", "SEMIABIERTO"

    def __init__(self, umbral_fallos: int = 5, espera_s: float = 30.0,
                 reloj: Callable[[], float] = time.monotonic) -> None:
        self.umbral_fallos = umbral_fallos
        self.espera_s = espera_s
        self._reloj = reloj
        self.estado = self.CERRADO
        self.aperturas = 0
        self.rechazadas = 0
        self._fallos = 0
        self._abierto_desde = 0.0
        self._sonda_en_curso = False

    def llamar(self, funcion: Callable, *args):
        self._permitir()
        try:
            resultado = funcion(*args)
        except TimeoutError:
            self._al_fallar(self._reloj())
            raise
        self._al_acertar(self._reloj())
        return resultado

    def _permitir(self) -> None:
        self._aplicar_resultados(self._reloj())
        if self.estado == self.ABIERTO:
            if self._reloj() - self._abierto_desde < self.espera_s:
                self.rechazadas += 1
                raise CircuitoAbierto()
            self.estado = self.SEMIABIERTO
        if self.estado == self.SEMIABIERTO:
            if self._sonda_en_curso:          # solo una llamada de prueba a la vez
                self.rechazadas += 1
                raise CircuitoAbierto()
            self._sonda_en_curso = True

    def _al_fallar(self, t: float) -> None:
        self._sonda_en_curso = False
        self._fallos += 1
        if self.estado == self.SEMIABIERTO or self._fallos >= self.umbral_fallos:
            self.estado = self.ABIERTO
            self._abierto_desde = t
            self._fallos = 0
            self.aperturas += 1

    def _al_acertar(self, t: float) -> None:
        self._sonda_en_curso = False
        self._fallos = 0
        self.estado = self.CERRADO

    def _aplicar_resultados(self, ahora: float) -> None:
        """Gancho para la simulación (aplicar resultados cuando la llamada termina)."""


class ValidadorConReintentos(ValidadorIdentidad):
    """Decorator: reintenta solo ante TimeoutError (misma regla que ConReintentos)."""

    def __init__(self, validador: ValidadorIdentidad, max_intentos: int = 3) -> None:
        self._validador = validador
        self._max_intentos = max_intentos

    def validar_dni(self, dni: str) -> bool:
        for intento in range(1, self._max_intentos + 1):
            try:
                return self._validador.validar_dni(dni)
            except TimeoutError:
                if intento == self._max_intentos:
                    raise
        raise AssertionError("inalcanzable")


class ValidadorConCircuitBreaker(ValidadorIdentidad):
    """Decorator: si el DNI falla seguido, deja de llamarlo y falla rápido."""

    def __init__(self, validador: ValidadorIdentidad, breaker: CircuitBreaker) -> None:
        self._validador = validador
        self.breaker = breaker

    def validar_dni(self, dni: str) -> bool:
        return self.breaker.llamar(self._validador.validar_dni, dni)


class ValidadorConDegradacion(ValidadorIdentidad):
    """Decorator: si el DNI no responde, acepta la reserva de forma provisional.

    El DNI queda en `pendientes` y se valida al volver el servicio con
    `revalidar_pendientes()`. Trade-off: puede aceptarse una reserva con DNI inválido,
    que luego hay que cancelar.
    """

    def __init__(self, validador: ValidadorIdentidad) -> None:
        self._validador = validador
        self.pendientes: list[str] = []

    def validar_dni(self, dni: str) -> bool:
        try:
            return self._validador.validar_dni(dni)
        except (TimeoutError, CircuitoAbierto):
            self.pendientes.append(dni)
            return True

    def revalidar_pendientes(self) -> list[str]:
        """Valida los DNI pendientes; devuelve los inválidos (reservas por cancelar).

        Los que siguen sin respuesta se conservan para el siguiente intento.
        """
        invalidos, siguen = [], []
        for dni in self.pendientes:
            try:
                if not self._validador.validar_dni(dni):
                    invalidos.append(dni)
            except (TimeoutError, CircuitoAbierto):
                siguen.append(dni)
        self.pendientes = siguen
        return invalidos