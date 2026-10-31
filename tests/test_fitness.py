"""Fitness functions de calidad (Lab 08, E5): FF-03 rendimiento y FF-04 disponibilidad.

Las estructurales (FF-01, FF-02) las verifica import-linter con .importlinter.
Estas fallan si una decisión de la iteración 1 o 2 se degrada.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fitness"))

import disponibilidad  # noqa: E402
import rendimiento  # noqa: E402

from src.reservas.adaptadores import DniAdapter  # noqa: E402
from src.reservas.resiliencia import (  # noqa: E402
    CircuitBreaker, ValidadorConCircuitBreaker, ValidadorConDegradacion,
    ValidadorConReintentos,
)


# ---------- FF-03: rendimiento (QA-01, p95 <= 1 s a 360 req/s) ----------
def test_ff03_indice_mas_cache_cumple_el_presupuesto_en_el_pico_8x():
    p95 = rendimiento.simular(360, rendimiento.WORKERS,
                              rendimiento.ESCENARIOS["Índice + caché"])["p95"]
    assert p95 <= rendimiento.PRESUPUESTO_P95_MS


def test_ff03_sin_cache_el_pico_8x_incumple_el_presupuesto():
    """Si alguien quita la caché, la fitness function lo detecta."""
    p95 = rendimiento.simular(360, rendimiento.WORKERS,
                              rendimiento.ESCENARIOS["Índice en BD"])["p95"]
    assert p95 > rendimiento.PRESUPUESTO_P95_MS


# ---------- FF-04: disponibilidad (QA-02, 0 perdidas y p95 <= 2 s) ----------
def test_ff04_modelo_breaker_y_degradacion_no_pierde_reservas():
    perdidas, _, latencias = disponibilidad.breaker_y_degradacion()
    assert perdidas == 0
    assert disponibilidad.p95(latencias) * 1000 <= 2000


def test_ff04_modelo_sin_tacticas_si_pierde_reservas():
    perdidas, _, _ = disponibilidad.sin_tacticas()
    assert perdidas > 0


class _DniCaido:
    """SDK del DNI caído: toda consulta agota el tiempo."""

    def __init__(self):
        self.llamadas = 0

    def consultar(self, dni):
        self.llamadas += 1
        raise TimeoutError()


def test_ff04_clases_reales_no_pierden_ninguna_reserva_con_el_dni_caido():
    sdk = _DniCaido()
    validador = ValidadorConDegradacion(
        ValidadorConCircuitBreaker(
            ValidadorConReintentos(DniAdapter(sdk)),
            CircuitBreaker(umbral_fallos=5, espera_s=30.0, reloj=lambda: 0.0),
        )
    )
    for _ in range(1000):
        assert validador.validar_dni("12345678") is True   # nunca lanza
    assert len(validador.pendientes) == 1000
    assert sdk.llamadas < 100                               # el breaker frena las llamadas