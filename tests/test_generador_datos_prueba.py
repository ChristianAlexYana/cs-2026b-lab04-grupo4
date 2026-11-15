"""E6: el generador acepta una salida válida y rechaza las inválidas (proveedor grabado, sin red)."""
import json

import pytest

from src.reservas.generador_datos_prueba import GeneradorDatosPrueba, ProveedorGrabado, SalidaInvalida
from src.reservas.ia import ProveedorLLM


class Fijo(ProveedorLLM):
    def __init__(self, texto): self._t = texto
    def completar(self, prompt): return self._t


def test_b1_v3_se_acepta():
    lote = GeneradorDatosPrueba(ProveedorGrabado("v3", "B1")).generar("pedido B1")
    assert lote["totales"]["pacientes"] == len(lote["pacientes"])
    assert all(p["es_ficticio"] for p in lote["pacientes"])


def test_b8_v3_se_rechaza_por_dni_de_ocho_digitos():
    with pytest.raises(SalidaInvalida):
        GeneradorDatosPrueba(ProveedorGrabado("v3", "B8")).generar("pedido B8")


def test_texto_que_no_es_json_se_rechaza():
    with pytest.raises(SalidaInvalida):
        GeneradorDatosPrueba(Fijo("LISTO")).generar("x")


def test_cita_con_paciente_inexistente_se_rechaza():
    lote = GeneradorDatosPrueba(ProveedorGrabado("v3", "B1")).generar("x")
    lote["citas"][0]["paciente_id"] = "P-9999"
    with pytest.raises(SalidaInvalida):
        GeneradorDatosPrueba(Fijo(json.dumps(lote))).generar("x")


def test_la_plantilla_recibe_el_pedido():
    vistos = []
    class Espia(ProveedorLLM):
        def completar(self, prompt):
            vistos.append(prompt); return "{}"
    with pytest.raises(SalidaInvalida):
        GeneradorDatosPrueba(Espia()).generar("PEDIDO-UNICO-123")
    assert "PEDIDO-UNICO-123" in vistos[0]
