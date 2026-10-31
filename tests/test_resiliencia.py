"""Pruebas de las tácticas de disponibilidad del DNI (Lab 08, iteración 2, QA-02)."""
import pytest

from src.reservas.puertos import ValidadorIdentidad
from src.reservas.resiliencia import (
    CircuitBreaker, CircuitoAbierto, ValidadorConCircuitBreaker,
    ValidadorConDegradacion, ValidadorConReintentos,
)


class DniFalso(ValidadorIdentidad):
    """Valida con una lista de respuestas: True/False o una excepción a lanzar."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = 0

    def validar_dni(self, dni):
        self.llamadas += 1
        r = self.respuestas.pop(0) if self.respuestas else True
        if isinstance(r, Exception):
            raise r
        return r


class RelojManual:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


# ---------- Reintentos ----------
def test_reintentos_se_recupera_de_un_timeout():
    falso = DniFalso([TimeoutError(), True])
    assert ValidadorConReintentos(falso).validar_dni("12345678") is True
    assert falso.llamadas == 2


def test_reintentos_no_reintenta_un_dni_rechazado():
    falso = DniFalso([False])
    assert ValidadorConReintentos(falso).validar_dni("1234") is False
    assert falso.llamadas == 1


def test_reintentos_propaga_timeout_al_agotar_intentos():
    falso = DniFalso([TimeoutError()] * 3)
    with pytest.raises(TimeoutError):
        ValidadorConReintentos(falso, max_intentos=3).validar_dni("12345678")
    assert falso.llamadas == 3


# ---------- Circuit breaker ----------
def _breaker_con_dni_caido(umbral=3, espera=30.0):
    reloj = RelojManual()
    falso = DniFalso([TimeoutError()] * 100)
    breaker = CircuitBreaker(umbral_fallos=umbral, espera_s=espera, reloj=reloj)
    return ValidadorConCircuitBreaker(falso, breaker), falso, breaker, reloj


def test_breaker_abre_tras_el_umbral_y_deja_de_llamar_al_dni():
    validador, falso, breaker, _ = _breaker_con_dni_caido(umbral=3)
    for _ in range(3):
        with pytest.raises(TimeoutError):
            validador.validar_dni("12345678")
    assert breaker.estado == CircuitBreaker.ABIERTO

    with pytest.raises(CircuitoAbierto):
        validador.validar_dni("12345678")
    assert falso.llamadas == 3                      # la 4.ª ni llegó al proveedor
    assert breaker.rechazadas == 1


def test_breaker_prueba_de_nuevo_y_cierra_cuando_el_dni_vuelve():
    validador, falso, breaker, reloj = _breaker_con_dni_caido(umbral=2, espera=30.0)
    for _ in range(2):
        with pytest.raises(TimeoutError):
            validador.validar_dni("12345678")
    reloj.t = 31.0
    falso.respuestas = [True]                       # el DNI se recuperó
    assert validador.validar_dni("12345678") is True
    assert breaker.estado == CircuitBreaker.CERRADO


def test_breaker_vuelve_a_abrir_si_la_prueba_falla():
    validador, _, breaker, reloj = _breaker_con_dni_caido(umbral=2, espera=30.0)
    for _ in range(2):
        with pytest.raises(TimeoutError):
            validador.validar_dni("12345678")
    reloj.t = 31.0
    with pytest.raises(TimeoutError):               # sigue caído: la prueba falla
        validador.validar_dni("12345678")
    assert breaker.estado == CircuitBreaker.ABIERTO
    assert breaker.aperturas == 2


def test_breaker_no_cuenta_un_dni_rechazado_como_fallo_del_proveedor():
    reloj = RelojManual()
    breaker = CircuitBreaker(umbral_fallos=2, reloj=reloj)
    validador = ValidadorConCircuitBreaker(DniFalso([False] * 5), breaker)
    for _ in range(5):
        assert validador.validar_dni("1234") is False
    assert breaker.estado == CircuitBreaker.CERRADO


# ---------- Degradación elegante ----------
def test_degradacion_acepta_provisional_y_no_pierde_la_reserva():
    degradado = ValidadorConDegradacion(DniFalso([TimeoutError()]))
    assert degradado.validar_dni("12345678") is True
    assert degradado.pendientes == ["12345678"]


def test_degradacion_tambien_cubre_el_breaker_abierto():
    validador, _, _, _ = _breaker_con_dni_caido(umbral=1)
    degradado = ValidadorConDegradacion(validador)
    for dni in ("11111111", "22222222", "33333333"):
        assert degradado.validar_dni(dni) is True   # nunca lanza
    assert len(degradado.pendientes) == 3


def test_revalidar_devuelve_los_dni_invalidos_para_cancelar():
    interno = DniFalso([TimeoutError(), TimeoutError()])
    degradado = ValidadorConDegradacion(interno)
    degradado.validar_dni("12345678")
    degradado.validar_dni("1234567")                # inválido (7 dígitos)
    interno.respuestas = [True, False]              # el DNI volvió
    assert degradado.revalidar_pendientes() == ["1234567"]
    assert degradado.pendientes == []


def test_revalidar_conserva_los_pendientes_si_el_dni_sigue_caido():
    interno = DniFalso([TimeoutError(), TimeoutError()])
    degradado = ValidadorConDegradacion(interno)
    degradado.validar_dni("12345678")
    assert degradado.revalidar_pendientes() == []
    assert degradado.pendientes == ["12345678"]