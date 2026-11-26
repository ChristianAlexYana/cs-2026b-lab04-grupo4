"""Convierte el tráfico JSON-RPC capturado por el espía en un diagrama de secuencia Mermaid
y en una tabla de métricas (mensajes, métodos, errores, latencia)."""
import collections, json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def cargar(archivo=RAIZ / "trazas/mcp_trafico.jsonl"):
    return [json.loads(l) for l in open(archivo, encoding="utf-8")]


def a_mermaid(eventos, aprobar=("reservar_cita_borrador",)) -> str:
    l = ["sequenceDiagram", "    autonumber", "    actor U as Humano", "    participant A as Agente (host MCP)",
         "    participant S as Servidor MCP citasalud"]
    pendientes = {}
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "host->servidor" and "method" in m:
            nombre = (m.get("params") or {}).get("name") or (m.get("params") or {}).get("uri") or ""
            if nombre in aprobar:
                l.append(f"    A->>U: ¿apruebas {nombre}?")
                l.append("    U-->>A: sí")
            pendientes[m.get("id")] = m["method"]
            l.append(f"    A->>S: {m['method']} {nombre}".rstrip())
        elif e["dir"] == "servidor->host" and "id" in m:
            r = m.get("result", {})
            if "error" in m or r.get("isError"):
                l.append("    S--xA: error (isError=true)")
            elif pendientes.get(m["id"]) == "server/discover":
                l.append(f"    S-->>A: versiones {', '.join(r.get('supportedVersions', []))} + capacidades")
            elif "tools" in r:
                l.append(f"    S-->>A: {len(r['tools'])} herramientas con esquema")
            else:
                l.append("    S-->>A: resultado (resultType=complete)")
    return "\n".join(l)


def metricas(eventos) -> dict:
    envios = {e["msg"]["id"]: e for e in eventos if e["dir"] == "host->servidor" and "id" in e["msg"]}
    lat = collections.defaultdict(list)
    errores = 0
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "servidor->host" and m.get("id") in envios:
            ida = envios[m["id"]]
            lat[ida["msg"]["method"]].append(round((e["t"] - ida["t"]) * 1000, 1))
            errores += bool(m.get("result", {}).get("isError") or "error" in m)
    return {"mensajes": len(eventos), "errores": errores, "latencia_ms": dict(lat),
            "bytes": sum(len(json.dumps(e["msg"])) for e in eventos)}


if __name__ == "__main__":
    ev = cargar()
    (RAIZ / "trazas/mcp_trafico.mmd").write_text(a_mermaid(ev), encoding="utf-8")
    print(json.dumps(metricas(ev), ensure_ascii=False, indent=1))
