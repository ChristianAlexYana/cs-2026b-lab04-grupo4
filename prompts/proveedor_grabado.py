"""Proveedor de promptfoo que devuelve respuestas grabadas (sin clave de API).

promptfoo entrega el prompt ya renderizado, no la ruta del archivo; por eso
la version se infiere de una huella estable del texto. Si un prompt cambia,
la huella debe actualizarse en el mismo commit.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent


def _version(prompt: str) -> str:
    if "# ROL" not in prompt:
        return "v1" if "JSON" not in prompt else "v2"
    return "v3.1" if "nombra los servicios externos" in prompt else "v3"


def call_api(prompt, options, context):
    version = _version(prompt)
    caso = context["vars"]["id"]
    archivo = RAIZ / "criterios" / "grabaciones" / version / f"{caso}.txt"
    if not archivo.exists():
        return {"error": f"Falta la grabacion {version}/{caso}.txt"}
    return {"output": archivo.read_text(encoding="utf-8")}