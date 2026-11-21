"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import ast
import pathlib
import re
import subprocess
import sys


class Herramientas:
    def __init__(self, raiz: str):
        self.raiz = pathlib.Path(raiz).resolve()

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta pytest y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
            "mapa_repo": "mapa_repo(): lista módulos Python y firmas de funciones sin leer sus cuerpos",
            "anotar": "anotar(texto): guarda una nota breve en notas.md dentro del sandbox",
            "leer_notas": "leer_notas(): devuelve las notas de esta corrida",
        }

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(str(p.relative_to(self.raiz)) for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz)}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def mapa_repo(self):
        salida = []
        for p in sorted(self.raiz.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            arbol = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            firmas = []
            for nodo in ast.walk(arbol):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    argumentos = [a.arg for a in nodo.args.posonlyargs + nodo.args.args + nodo.args.kwonlyargs]
                    if nodo.args.vararg:
                        argumentos.append("*" + nodo.args.vararg.arg)
                    if nodo.args.kwarg:
                        argumentos.append("**" + nodo.args.kwarg.arg)
                    firmas.append(f"  def {nodo.name}({', '.join(argumentos)})")
            salida.append("\n".join([str(p.relative_to(self.raiz)), *firmas]))
        return "\n".join(salida)

    def anotar(self, texto):
        if not isinstance(texto, str) or not texto.strip() or "\n" in texto or len(texto) > 300:
            return "ERROR: la nota debe ser una sola línea de 1 a 300 caracteres"
        p = self._ruta("notas.md")
        with p.open("a", encoding="utf-8") as archivo:
            archivo.write(f"- {texto.strip()}\n")
        return "OK: nota guardada"

    def leer_notas(self):
        p = self._ruta("notas.md")
        return p.read_text(encoding="utf-8") if p.exists() else "(sin notas)"

    def ejecutar_pruebas(self):
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=self.raiz, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original="../trabajo_original"):
        import difflib
        base, salida = self._ruta_libre(original), []
        for p in sorted(self.raiz.rglob("*.py")):
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel}", f"b/{rel}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        r = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]
