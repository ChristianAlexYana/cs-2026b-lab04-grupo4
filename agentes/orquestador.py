"""Multiagente por gestor + actor-crítico: Planificador -> [Ejecutor <-> Revisor] -> Humano (máx. 2 rondas). Para E5 y E6.

    python agentes/orquestador.py --issue 2 --etiqueta issue2_actor
E6: con --aprobar, cada edición del ejecutor pide su aprobación en consola ("s" o "n").
"""
import json
from comun import PROTOCOLO, argumentos, preparar_trabajo, modelo, traza, objetivo_issue, politica_ejecutor
from agente.nucleo import Agente
from agente.politica import Politica

MAX_RONDAS = 2

if __name__ == "__main__":
    args = argumentos(__doc__)
    h = preparar_trabajo()
    planificador = Agente("planificador", modelo(args, "planificador"), h, Politica(herramientas_permitidas=set(), max_pasos=2),
                          f"Planifica cómo resolver el issue {args.issue} de CitaSalud. {objetivo_issue(args.issue)}\n{PROTOCOLO}\nNo tienes herramientas; termina con final.", traza(args, "planificador"))
    plan = planificador.ejecutar()
    print(f"PLANIFICADOR:\n{plan}\n")
    agentes, retro = [planificador], ""
    for ronda in range(1, MAX_RONDAS + 1):
        ejecutor = Agente("ejecutor", modelo(args, "ejecutor", ronda), h, politica_ejecutor(args, 12),
                          f"{objetivo_issue(args.issue)}\n{PROTOCOLO}\nPlan:\n{plan}\n{retro}Herramientas: {h.catalogo()}", traza(args, "ejecutor", ronda))
        resumen = ejecutor.ejecutar()
        revisor = Agente("revisor", modelo(args, "revisor", ronda), h,
                         Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"}, max_pasos=8),
                         f"Revisa el cambio del ejecutor. Responde APROBADO... o CAMBIOS SOLICITADOS...\n"
                         f"{PROTOCOLO}\nHerramientas permitidas: ver_cambios, leer_archivo, buscar, ejecutar_pruebas.\n"
                         f"Resumen:\n{resumen}", traza(args, "revisor", ronda))
        veredicto = revisor.ejecutar()
        agentes += [ejecutor, revisor]
        print(f"--- RONDA {ronda}\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")
        if veredicto.startswith("APROBADO"):
            break
        retro = f"El revisor solicitó cambios:\n{veredicto}\n"
    print(f"Rondas actor-crítico: {ronda} de {MAX_RONDAS}. Decisión final: HUMANO (aprobar o rechazar el cambio).")
    for a in agentes:
        n = len(json.dumps(a.historial, ensure_ascii=False))
        print(f"[{a.nombre}] contexto final: {n} caracteres (~{n // 4} tokens)")
    print(f"Siguiente paso: python agentes/agente/traza.py agentes/trazas/{args.etiqueta}")
