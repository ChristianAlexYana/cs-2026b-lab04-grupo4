"""Piezas compartidas por ejecutar.py (agente único) y orquestador.py (actor-crítico) para CitaSalud."""
import argparse, pathlib, shutil, sys

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parent
sys.path.insert(0, str(AQUI))
from agente.herramientas import Herramientas       # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo   # noqa: E402

COPIAR = ("src", "tests", "issues", "prompts", "fitness", ".importlinter")   # lo que el agente ve
PROTOCOLO = ('Responde con UN objeto JSON en UNA línea: '
             '{"pensamiento":"...","accion":"<herramienta>","args":{...}} '
             'o {"pensamiento":"...","final":"<respuesta>"}. '
             'Usa accion o final, nunca ambos; espera la observación antes de decidir de nuevo.')


def argumentos(descripcion):
    ap = argparse.ArgumentParser(description=descripcion)
    ap.add_argument("--issue", type=int, required=True, help="número del issue (1, 2 o 3)")
    ap.add_argument("--etiqueta", required=True, help="nombre de la corrida, ej. issue1_unico, issue2_unico, issue2_actor")
    ap.add_argument("--modelo", choices=["interactivo", "grabado"], default="interactivo")
    ap.add_argument("--aprobar", action="store_true", help="E6: un humano aprueba o rechaza cada edición (s/n)")
    return ap.parse_args()


def aprobar_en_consola(args: dict) -> bool:
    """Humano en el circuito (Tabla 8): solo se acepta 's' o 'n'."""
    print(f"\n>>> El agente quiere editar {args.get('ruta')}:\n--- antes ---\n{args.get('antes')}\n--- después ---\n{args.get('despues')}")
    while True:
        r = input("¿Aprueba esta edición? (s/n): ").strip().lower()
        if r in ("s", "n"):
            return r == "s"


def politica_ejecutor(args, max_pasos):
    from agente.politica import Politica
    p = Politica(max_pasos=max_pasos)
    if args.aprobar:
        p.aprobar_edicion = aprobar_en_consola
    return p


def preparar_trabajo():
    """Cada corrida parte de una copia limpia del repositorio: el agente nunca toca el repo real."""
    for nombre in ("trabajo", "trabajo_original"):
        destino = AQUI / nombre
        shutil.rmtree(destino, ignore_errors=True)
        for item in COPIAR:
            origen = REPO / item
            if origen.is_dir():
                shutil.copytree(origen, destino / item, ignore=shutil.ignore_patterns("__pycache__", "*.html", "resultados.json"))
            elif origen.exists():
                destino.mkdir(exist_ok=True)
                shutil.copy(origen, destino / item)
    return Herramientas(AQUI / "trabajo")


def modelo(args, agente, ronda=1):
    """ModeloInteractivo: usted pega la respuesta JSON de su asistente y queda grabada. ModeloGrabado: la reproduce."""
    sufijo = "" if ronda == 1 else f"_r{ronda}"
    archivo = AQUI / "trayectorias" / args.etiqueta / f"{agente}{sufijo}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    return ModeloGrabado(archivo) if args.modelo == "grabado" else ModeloInteractivo(archivo)


def traza(args, agente, ronda=1):
    sufijo = "" if ronda == 1 else f"_r{ronda}"
    carpeta = AQUI / "trazas" / args.etiqueta
    carpeta.mkdir(parents=True, exist_ok=True)
    return str(carpeta / f"{agente}{sufijo}.jsonl")


def objetivo_issue(n):
    return f"Resuelve issues/ISSUE-0{n}.md en el repositorio de CitaSalud Arequipa. La prueba tests/test_issue_0{n}.py debe pasar y no debes editar tests/."
