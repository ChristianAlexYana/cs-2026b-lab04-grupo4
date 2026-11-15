"""Generador de datos de prueba sintéticos con IA (Lab 09, E6).

Va detrás del puerto ProveedorLLM (Lab 07). La respuesta del modelo es un dato NO confiable:
se valida con el esquema de la evaluación y con guardrails de ficción e integridad.
"""
import json
import pathlib

from jsonschema import Draft202012Validator

from .ia import ProveedorLLM

CARPETA = pathlib.Path(__file__).resolve().parents[2] / "prompts" / "datos-prueba"
ESQUEMA = json.loads((CARPETA / "esquema.json").read_text(encoding="utf-8"))
_VALIDADOR = Draft202012Validator(ESQUEMA)


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato o rompe un guardrail: se descarta."""


def _integridad(lote: dict) -> None:
    ids = [p["paciente_id"] for p in lote["pacientes"]]
    if len(ids) != len(set(ids)):
        raise SalidaInvalida("paciente_id repetido")
    citas = [c["cita_id"] for c in lote["citas"]]
    if len(citas) != len(set(citas)):
        raise SalidaInvalida("cita_id repetido")
    conocidos = set(ids)
    for c in lote["citas"]:
        if c["paciente_id"] not in conocidos:
            raise SalidaInvalida(f"la cita {c['cita_id']} apunta a un paciente inexistente")
    if lote["totales"] != {"pacientes": len(lote["pacientes"]), "citas": len(lote["citas"])}:
        raise SalidaInvalida("los totales no coinciden con el contenido")


def _ficcion(lote: dict) -> None:
    # Ley 29733: un DNI de 8 dígitos solo vale si es el rango ficticio 999#####; lo demás debe ser FICTICIO-####.
    for p in lote["pacientes"]:
        dni = p["dni"]
        if dni.isdigit() and not dni.startswith("999"):
            raise SalidaInvalida(f"DNI con formato real: {dni}")
        if p.get("es_ficticio") is not True:
            raise SalidaInvalida("paciente no marcado como ficticio")


class GeneradorDatosPrueba:
    def __init__(self, proveedor: ProveedorLLM, version: str = "v3") -> None:
        self._proveedor = proveedor
        self._plantilla = (CARPETA / f"{version}.txt").read_text(encoding="utf-8")
        self.version = version

    def generar(self, pedido: str) -> dict:
        prompt = self._plantilla.replace("{{pedido}}", pedido)
        texto = self._proveedor.completar(prompt)
        try:
            lote = json.loads(texto)
        except json.JSONDecodeError as e:
            raise SalidaInvalida(f"no es JSON: {e}") from e
        error = next(iter(_VALIDADOR.iter_errors(lote)), None)
        if error is not None:
            raise SalidaInvalida(f"contrato: {error.message[:120]}")
        _ficcion(lote)
        _integridad(lote)
        return lote


class ProveedorGrabado(ProveedorLLM):
    """Doble de prueba: devuelve una respuesta grabada (sin red ni claves)."""

    def __init__(self, version: str, caso: str) -> None:
        self._archivo = CARPETA / "grabaciones" / version / f"{caso}.txt"

    def completar(self, prompt: str) -> str:
        return self._archivo.read_text(encoding="utf-8").strip()
