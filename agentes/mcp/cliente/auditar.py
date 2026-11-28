"""Auditor básico de servidores MCP: revisa el catálogo ANTES de conectarlo a un host.
Uso: python cliente/auditar.py <servidor.py>     (código de salida 1 si hay hallazgos altos)"""
import asyncio, re, sys
from mcp import Client, StdioServerParameters

REGLAS = [  # (severidad, patrón en la descripción, explicación)
    ("ALTA", r"<\s*important\s*>|ignora|ignore (all|previous)|no (le )?(menciones|digas)|do not (tell|mention)",
     "instrucciones ocultas dirigidas al modelo"),
    ("ALTA", r"\.env\b|id_rsa|\.ssh|credencial|password|contraseña|token|api[_ ]?key", "pide secretos o credenciales"),
    ("ALTA", r"curl |wget |\| *sh\b|https?://", "comandos o URL externas en la descripción"),
    ("MEDIA", r"(lee|read).{0,40}(archivo|file|recurso|resource)", "pide leer datos ajenos a su función"),
]
PARAMS_SOSPECHOSOS = {"contexto", "context", "notas", "notes", "extra", "metadata", "debug"}


def hallazgos_de(tool) -> list:
    """Revisa UNA herramienta del catálogo y devuelve [(severidad, nombre, motivo)]."""
    hallazgos, desc = [], tool.description or ""
    for sev, patron, motivo in REGLAS:
        if re.search(patron, desc, re.I):
            hallazgos.append((sev, tool.name, motivo))
    props = tool.input_schema.get("properties", {})
    for p in set(props) & PARAMS_SOSPECHOSOS:
        hallazgos.append(("MEDIA", tool.name, f"parámetro genérico '{p}' que podría usarse para filtrar datos"))
    anot = tool.annotations
    if anot is None:
        hallazgos.append(("BAJA", tool.name, "sin anotaciones (¿solo lectura? ¿destructiva?)"))
    elif anot.read_only_hint is not True and anot.destructive_hint is None:
        # Regla nueva 1 (E7): si no es de solo lectura y no declara destructiveHint, el protocolo asume destructiva.
        hallazgos.append(("MEDIA", tool.name, "escritura sin destructiveHint explícito (se asume destructiva)"))
    if len(desc) > 400:
        hallazgos.append(("BAJA", tool.name, f"descripción muy larga ({len(desc)} caracteres)"))
    # Regla nueva 2 (E7): texto libre que el esquema no acota (sin maxLength, enum ni pattern).
    libres = sorted(n for n, d in props.items()
                    if d.get("type") == "string" and not ({"maxLength", "enum", "pattern", "const"} & set(d)))
    if libres:
        hallazgos.append(("BAJA", tool.name, f"texto libre sin límite en el esquema: {', '.join(libres)}"))
    return hallazgos


async def auditar(ruta):
    hallazgos = []
    async with Client(StdioServerParameters(command=sys.executable, args=[ruta])) as c:
        for t in (await c.list_tools()).tools:
            hallazgos += hallazgos_de(t)
        print(f"Servidor: {c.server_info.name}")
    for h in hallazgos or [("OK", "-", "sin hallazgos")]:
        print(f"  [{h[0]:<5}] {h[1]:<22} {h[2]}")
    return any(h[0] == "ALTA" for h in hallazgos)


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(auditar(sys.argv[1])) else 0)
