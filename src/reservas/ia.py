"""IA aislada (E5): el LLM es un componente no determinista detrás de una interfaz."""
from abc import ABC, abstractmethod


class ProveedorLLM(ABC):
    @abstractmethod
    def completar(self, prompt: str) -> str: ...


class LLMSimuladoSDK:
    """SDK simulado: sin red ni claves. Su interfaz es distinta a ProveedorLLM a propósito."""

    def __init__(self, respuesta: str = "Medicina General") -> None:
        self.respuesta = respuesta
        self.llamadas = 0

    def generar(self, entrada: str) -> dict:
        self.llamadas += 1
        return {"ok": True, "salida": self.respuesta}


class LLMSimuladoAdapter(ProveedorLLM):
    """Adapter: traduce el SDK simulado al puerto ProveedorLLM."""

    def __init__(self, sdk: LLMSimuladoSDK) -> None:
        self._sdk = sdk

    def completar(self, prompt: str) -> str:
        res = self._sdk.generar(prompt)
        if not res.get("ok"):
            raise ValueError("Fallo del proveedor LLM")
        return res["salida"]


class ClasificadorMotivo:
    """Sugiere una especialidad según el motivo de consulta (sin diagnosticar)."""

    def __init__(self, proveedor: ProveedorLLM) -> None:
        self._proveedor = proveedor

    def sugerir_especialidad(self, motivo: str) -> str:
        prompt = (
            "Sugiere solo el nombre de la especialidad médica para este motivo "
            f"de consulta, sin diagnosticar: {motivo}"
        )
        return self._proveedor.completar(prompt)

class ConCache(ProveedorLLM):
    """Decorator: guarda las respuestas de prompts repetidos para evitar llamadas."""

    def __init__(self, proveedor: ProveedorLLM) -> None:
        self._proveedor = proveedor
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._proveedor.completar(prompt)
        return self._cache[prompt]

ESPECIALIDADES = {"Medicina General", "Cardiologia", "Pediatria", "Dermatologia", "Ginecologia"}


class Guardrail(ABC):
    """Chain of Responsibility: cada eslabón valida y pasa la respuesta al siguiente."""

    def __init__(self, siguiente: "Guardrail | None" = None) -> None:
        self._siguiente = siguiente

    def validar(self, respuesta: str) -> str:
        self._revisar(respuesta)
        if self._siguiente is not None:
            return self._siguiente.validar(respuesta)
        return respuesta

    @abstractmethod
    def _revisar(self, respuesta: str) -> None: ...


class LongitudMaxima(Guardrail):
    def __init__(self, maximo: int = 40, siguiente: "Guardrail | None" = None) -> None:
        super().__init__(siguiente)
        self._maximo = maximo

    def _revisar(self, respuesta: str) -> None:
        if len(respuesta) > self._maximo:
            raise ValueError("Respuesta bloqueada: demasiado larga")


class SinDiagnosticos(Guardrail):
    FRASES = ("diagnostico", "diagnóstico", "usted tiene", "padece", "sufre de")

    def _revisar(self, respuesta: str) -> None:
        if any(frase in respuesta.lower() for frase in self.FRASES):
            raise ValueError("Respuesta bloqueada: contiene un diagnóstico")


class EspecialidadValida(Guardrail):
    def __init__(self, catalogo=ESPECIALIDADES, siguiente: "Guardrail | None" = None) -> None:
        super().__init__(siguiente)
        self._catalogo = catalogo

    def _revisar(self, respuesta: str) -> None:
        if respuesta not in self._catalogo:
            raise ValueError("Respuesta bloqueada: la especialidad no está en el catálogo")


def crear_cadena_guardrails() -> Guardrail:
    return LongitudMaxima(siguiente=SinDiagnosticos(siguiente=EspecialidadValida()))


class ConGuardrails(ProveedorLLM):
    """Decorator: la salida del LLM es dato no confiable; se valida antes de usarla."""

    def __init__(self, proveedor: ProveedorLLM, cadena: Guardrail) -> None:
        self._proveedor = proveedor
        self._cadena = cadena

    def completar(self, prompt: str) -> str:
        return self._cadena.validar(self._proveedor.completar(prompt))