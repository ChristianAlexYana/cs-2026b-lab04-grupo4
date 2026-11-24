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


async def auditar(ruta):
    hallazgos = []
    async with Client(StdioServerParameters(command=sys.executable, args=[ruta])) as c:
        for t in (await c.list_tools()).tools:
            desc = t.description or ""
            for sev, patron, motivo in REGLAS:
                if re.search(patron, desc, re.I):
                    hallazgos.append((sev, t.name, motivo))
            for p in set(t.input_schema.get("properties", {})) & PARAMS_SOSPECHOSOS:
                hallazgos.append(("MEDIA", t.name, f"parámetro genérico '{p}' que podría usarse para filtrar datos"))
            if t.annotations is None:
                hallazgos.append(("BAJA", t.name, "sin anotaciones (¿solo lectura? ¿destructiva?)"))
            if len(desc) > 400:
                hallazgos.append(("BAJA", t.name, f"descripción muy larga ({len(desc)} caracteres)"))
        print(f"Servidor: {c.server_info.name}")
    for h in hallazgos or [("OK", "-", "sin hallazgos")]:
        print(f"  [{h[0]:<5}] {h[1]:<22} {h[2]}")
    return any(h[0] == "ALTA" for h in hallazgos)


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(auditar(sys.argv[1])) else 0)
