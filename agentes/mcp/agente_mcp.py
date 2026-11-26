"""E4: el agente del Lab 10 usando el servidor MCP de CitaSalud. El núcleo del agente no cambia.
Las decisiones las da su asistente (ModeloInteractivo: copia el contexto, pega el JSON en UNA línea) o se
repiten desde una grabación. La escritura (reservar_cita_borrador) pasa por aprobación humana en consola.

    python agentes/mcp/agente_mcp.py --etiqueta consulta1
    python agentes/mcp/agente_mcp.py --etiqueta consulta1 --modelo grabado
Deja: trayectorias/<etiqueta>.json, trazas/<etiqueta>/agente.jsonl, mcp_trafico.jsonl y trafico.mmd."""
import argparse, json, pathlib, shutil, sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "agentes"), str(AQUI / "cliente")]
from mcp import StdioServerParameters                       # noqa: E402
from agente.nucleo import Agente                             # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo  # noqa: E402
from agente.politica import Politica                         # noqa: E402
from agente.herramientas_mcp import HerramientasMCP          # noqa: E402
import traza_mcp                                             # noqa: E402

OBJETIVO = ("La coordinadora de CitaSalud pregunta: ¿cuántas citas del 2026-11-23 se cancelaron y qué especialidades "
            "tienen cupo directo? Si Medicina General tiene cupo, crea un borrador de reserva para el DNI 99900001, "
            "celular 999000001.")
PROTOCOLO = ('Responde con UN objeto JSON en UNA línea: {"pensamiento":"...","accion":"<herramienta>","args":{...}} '
             'o {"pensamiento":"...","final":"<respuesta>"}. Usa accion o final, nunca ambos; '
             'espera la observación antes de decidir de nuevo.')


def aprobar_en_consola(accion, args) -> bool:
    """Humano en el circuito: solo se acepta 's' o 'n'."""
    print(f"\n>>> El agente quiere ejecutar la herramienta de ESCRITURA {accion} con {args}")
    while True:
        r = input("¿Aprueba? (s/n): ").strip().lower()
        if r in ("s", "n"):
            return r == "s"


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--etiqueta", required=True)
ap.add_argument("--modelo", choices=["interactivo", "grabado"], default="interactivo")
ap.add_argument("--objetivo", default=OBJETIVO)
ap.add_argument("--auto-aprobar", action="store_true", help="solo para pruebas automáticas; no use en la entrega")
args = ap.parse_args()

(AQUI / "trayectorias").mkdir(exist_ok=True)
salida = AQUI / "trazas" / args.etiqueta
salida.mkdir(parents=True, exist_ok=True)
trafico = AQUI / "trazas" / "mcp_trafico.jsonl"
trafico.unlink(missing_ok=True)

h = HerramientasMCP(StdioServerParameters(command=sys.executable,
                    args=[str(AQUI / "cliente/espia.py"), str(AQUI / "servidor_mcp/citasalud_mcp.py")]))
print("Herramientas descubiertas por MCP:", ", ".join(h.catalogo()))
print("Requieren aprobación (según anotaciones):", h.herramientas_de_escritura())
politica = Politica(herramientas_permitidas=set(h.catalogo()), max_pasos=10,
                    requieren_aprobacion=h.herramientas_de_escritura())
politica.aprobar = (lambda a, x: True) if args.auto_aprobar else aprobar_en_consola
archivo = AQUI / "trayectorias" / f"{args.etiqueta}.json"
modelo = ModeloGrabado(archivo) if args.modelo == "grabado" else ModeloInteractivo(archivo)
agente = Agente("agente_citas", modelo, h, politica,
                f"{args.objetivo}\n{PROTOCOLO}\nHerramientas disponibles: {h.catalogo()}", str(salida / "agente.jsonl"))
print("\nRESPUESTA FINAL:\n" + agente.ejecutar())
for e in agente.eventos:
    if e["tipo"] == "accion":
        print(f"  paso {e['paso']}: {e['accion']:<22} {e['estado']:<12} {e['observacion'][:70]!r}")
h.cerrar()
if trafico.exists():
    shutil.move(str(trafico), salida / "mcp_trafico.jsonl")
    ev = traza_mcp.cargar(salida / "mcp_trafico.jsonl")
    (salida / "trafico.mmd").write_text(traza_mcp.a_mermaid(ev), encoding="utf-8")
    print("\nMétricas JSON-RPC:", json.dumps(traza_mcp.metricas(ev), ensure_ascii=False))
    print(f"Diagrama: {(salida / 'trafico.mmd').relative_to(RAIZ)}")
