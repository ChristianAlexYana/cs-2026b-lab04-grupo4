"""Explora CitaSalud por stdio y verifica consultas de solo lectura."""

import asyncio
import json
import pathlib
import sys

from mcp import Client, StdioServerParameters
from mcp.types import Implementation

SERVIDOR = pathlib.Path(__file__).resolve().parents[1] / "servidor_mcp/citasalud_mcp.py"


def _json(datos: object) -> str:
    return json.dumps(datos, ensure_ascii=False)


async def main() -> None:
    parametros = StdioServerParameters(command=sys.executable, args=["-B", str(SERVIDOR.resolve())])
    async with Client(
        parametros,
        client_info=Implementation(name="explorador-citasalud", version="1.0"),
        read_timeout_seconds=10,
    ) as cliente:
        print(f"Servidor: {cliente.server_info.name} | Protocolo: {cliente.protocol_version}")

        print("\ntools/list")
        herramientas = (await cliente.list_tools()).tools
        for herramienta in herramientas:
            argumentos = ", ".join(herramienta.input_schema["properties"])
            anotaciones = herramienta.annotations.model_dump(by_alias=True, exclude_none=True)
            print(f"  {herramienta.name}({argumentos})")
            print("    annotations:", _json(anotaciones))
            print("    outputSchema:", _json(herramienta.output_schema))

        cupos = next(herramienta for herramienta in herramientas if herramienta.name == "cupos_disponibles")
        if not cupos.output_schema or set(cupos.output_schema.get("required", [])) != {"especialidad", "disponible"}:
            raise RuntimeError("Falta el outputSchema esperado para cupos_disponibles.")

        print("\nresources/list")
        for recurso in (await cliente.list_resources()).resources:
            print(f"  {recurso.uri}  {recurso.title}")

        print("\nresources/templates/list")
        for plantilla in (await cliente.list_resource_templates()).resource_templates:
            print(f"  {plantilla.uri_template}  {plantilla.title}")

        print("\nprompts/list")
        for prompt in (await cliente.list_prompts()).prompts:
            argumentos = ", ".join(argumento.name for argumento in prompt.arguments or [])
            print(f"  {prompt.name}({argumentos})")

        print("\nLecturas por stdio")
        resultado = await cliente.call_tool("cupos_disponibles", {"especialidad": "Medicina General"})
        if resultado.is_error or resultado.structured_content != {"especialidad": "Medicina General", "disponible": True}:
            raise RuntimeError("cupos_disponibles no devolvió el contenido estructurado esperado.")
        print("  cupos_disponibles · structuredContent:", _json(resultado.structured_content))

        invalido = await cliente.call_tool("cupos_disponibles", {"especialidad": "Especialidad inexistente"})
        error = " ".join(getattr(bloque, "text", "") for bloque in invalido.content)
        if not invalido.is_error or "Medicina General" not in error or "Cardiologia" not in error:
            raise RuntimeError("La especialidad inválida no devolvió el error esperado.")
        print(f"  cupos_disponibles · is_error={invalido.is_error} | {error}")

        fecha = "2026-11-23"
        agenda = await cliente.call_tool("citas_del_dia", {"fecha": fecha})
        if agenda.is_error or agenda.structured_content != {"fecha": fecha, "estado": "SIN_FUENTE"}:
            raise RuntimeError("citas_del_dia no informó la falta de fuente de agenda.")
        print("  citas_del_dia · structuredContent:", _json(agenda.structured_content))

        dni = await cliente.call_tool("validar_dni", {"dni": "99900001"})
        if dni.is_error or dni.structured_content != {"result": True}:
            raise RuntimeError("El adaptador no aceptó el DNI sintético de prueba.")
        print("  validar_dni · structuredContent:", _json(dni.structured_content))

        adr = await cliente.read_resource("citasalud://adr/001")
        print("  resources/read · adr/001:", adr.contents[0].text.splitlines()[0])

        resumen = await cliente.get_prompt("resumen_del_dia", {"fecha": fecha})
        print("  prompts/get · resumen_del_dia:", resumen.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
