"""Guardrails: qué puede hacer el agente, cuántas veces y con qué aprobación."""
import re
from pathlib import PurePath
from dataclasses import dataclass, field


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo", "ejecutar_comando",
        "mapa_repo", "anotar", "leer_notas"})
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)          # el agente no puede "arreglar" las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion = None                          # función opcional: humano en el circuito (human-in-the-loop)

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if (not isinstance(cmd, str) or any(c in cmd for c in ";|&`$><\n\r")
                    or not any(re.search(p, cmd) for p in self.comandos_permitidos)):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            if (not isinstance(ruta, str) or PurePath(ruta).is_absolute()
                    or ".." in PurePath(ruta).parts
                    or any(PurePath(ruta).parts[:1] == (protegida.strip("/"),)
                           for protegida in self.rutas_protegidas)):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
