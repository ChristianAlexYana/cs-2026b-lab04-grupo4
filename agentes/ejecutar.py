"""Agente ÚNICO (ReAct) sobre un issue. Úselo para E2 (issue 1), E4 (issue 3) y la variante 'único' de E5 (issue 2).

    python agentes/ejecutar.py --issue 1 --etiqueta issue1_unico
Con ModeloInteractivo la consola imprime el contexto; cópielo en su asistente, pegue la respuesta JSON (una línea)
y la decisión queda grabada en agentes/trayectorias/<etiqueta>/ejecutor.json.
E6: agregue --aprobar para que usted apruebe o rechace cada edición (s/n).
"""
from comun import argumentos, preparar_trabajo, modelo, traza, objetivo_issue, politica_ejecutor
from agente.nucleo import Agente

args = argumentos(__doc__)
h = preparar_trabajo()
contexto = f"{objetivo_issue(args.issue)}\nHerramientas disponibles: {h.catalogo()}"
ejecutor = Agente("ejecutor", modelo(args, "ejecutor"), h, politica_ejecutor(args, 15), contexto, traza(args, "ejecutor"))
print(f"\nRESPUESTA FINAL: {ejecutor.ejecutar()}")
n = len(str(ejecutor.historial))
print(f"[ejecutor] contexto final: {n} caracteres (~{n // 4} tokens)")
print(f"Siguiente paso: python agentes/agente/traza.py agentes/trazas/{args.etiqueta}")
