"""E6: mide cuánto contexto consume el catálogo MCP (lo que el host manda al modelo en cada turno).
Uso: python agentes/mcp/cliente/costo_catalogo.py [servidor.py]      (aproximación: 1 token ≈ 4 caracteres)"""
import asyncio, json, pathlib, sys
from mcp import Client, StdioServerParameters

RAIZ = pathlib.Path(__file__).resolve().parents[1]
RUTA = sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "servidor_mcp/citasalud_mcp.py")
SERVIDOR = StdioServerParameters(command=sys.executable, args=[RUTA])


async def main():
    async with Client(SERVIDOR) as c:
        tools = (await c.list_tools()).tools
    total = 0
    print(f"{'herramienta':<26}{'caracteres':>11}{'~tokens':>9}")
    for t in tools:
        n = len(json.dumps({"name": t.name, "description": t.description, "inputSchema": t.input_schema,
                            "outputSchema": t.output_schema}, ensure_ascii=False))
        total += n
        print(f"{t.name:<26}{n:>11}{n // 4:>9}")
    print(f"{'TOTAL':<26}{total:>11}{total // 4:>9}   ({len(tools)} herramientas)")


asyncio.run(main())
