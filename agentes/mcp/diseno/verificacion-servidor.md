# Verificación del servidor MCP de CitaSalud

Lab 11 · Grupo 04 · E2

## Ejecución

Desde la raíz del repositorio, usa Python del entorno del proyecto. El cliente y el servidor usan `mcp==2.3.0`, la versión verificada del SDK oficial. Para instalar las dependencias del MCP en el entorno, ejecuta `.venv/bin/python -m pip install -r agentes/mcp/requirements.txt`.

```sh
.venv/bin/python -m compileall -q agentes/mcp/servidor_mcp agentes/mcp/cliente
.venv/bin/python agentes/mcp/cliente/explorar.py
.venv/bin/python -m pytest -q
```

`explorar.py` abre el servidor con el mismo intérprete, usa una ruta absoluta y se conecta directamente por stdio. Imprime las listas de herramientas con sus anotaciones y `outputSchema`, los recursos, las plantillas y los prompts. El servidor reserva stdout para el protocolo y registra sus mensajes en stderr. El explorador solo hace lecturas y conserva las trazas existentes.

## Firmas y entradas

```python
cupos_disponibles(especialidad: str) -> CupoDisponible
citas_del_dia(fecha: str) -> ConsultaCitasDelDia
validar_dni(dni: str) -> bool
reservar_cita_borrador(dni: str, especialidad: str, celular: str) -> str
```

| Llamada | Argumentos de prueba para E5 |
|---|---|
| `cupos_disponibles` | `{"especialidad": "Medicina General"}` |
| `citas_del_dia` | `{"fecha": "2026-11-23"}` |
| `validar_dni` | `{"dni": "99900001"}` |
| `reservar_cita_borrador` | `{"dni": "99900001", "especialidad": "Medicina General", "celular": "999000001"}`. Requiere aprobación humana previa en el host. |
| `resources/read` | `{"uri": "citasalud://adr/001"}` |

`cupos_disponibles` y `citas_del_dia` publican objetos tipados. En Python, el SDK expone `tool.output_schema` y `result.structured_content`. El SDK envuelve el `bool` de `validar_dni` en el campo `result`. Para la escritura, la salida es texto con el nombre `BORRADOR-NN.md`.

## Resultados observados

- `compileall` terminó con código 0.
- El cliente negoció el protocolo `2026-07-28`. `cupos_disponibles` publicó un `outputSchema` con `especialidad` y `disponible` obligatorios y devolvió `{"especialidad": "Medicina General", "disponible": true}` en `structuredContent`.
- La especialidad inexistente devolvió `is_error=True` e indicó las claves válidas `Medicina General` y `Cardiologia`.
- `citas_del_dia` devolvió `{"fecha": "2026-11-23", "estado": "SIN_FUENTE"}`. El cliente leyó el ADR-001 y obtuvo `resumen_del_dia(fecha="2026-11-23")`.
- `validar_dni` devolvió `{"result": true}` para el ejemplo sintético. Se comprobó directamente el rechazo de fechas imposibles o mal formadas, DNI con dígitos Unicode o longitud inválida, números de ADR fuera de la lista y un ID de historia demasiado largo.
- `pytest` pasó las 77 pruebas existentes en 0,20 s. La llamada de escritura queda para E5.

Dentro del sandbox de ejecución se bloqueó una operación mínima de `asyncio` con hilos. La conexión se verificó fuera de ese sandbox. Para evitar cambios en las cachés del repositorio se usaron `PYTHONPYCACHEPREFIX` en `/tmp` al compilar y `PYTHONDONTWRITEBYTECODE=1` al ejecutar las pruebas.

## Límites del contrato

- El servicio de reservas mantiene dos booleanos de disponibilidad directa en memoria. La consulta usa las claves exactas de `cupos_db` y carece de filtro por fecha.
- La `Cita` que recibe `ServicioReservasDespues` carece de fecha de atención y el servicio carece de un repositorio de citas. `SIN_FUENTE` significa que la agenda está indisponible. La consulta devuelve cero filas de datos y no informa un recuento de citas. Una fecha imposible o con formato distinto de `AAAA-MM-DD` se rechaza.
- El DNI de prueba debe ajustarse a `999[0-9]{5}` y se valida con el `DniAdapter` predeterminado. La `Cita` guarda el celular como texto. El MCP adopta el formato de prueba `999[0-9]{6}` del Lab 09. Los errores de formato de las herramientas omiten los valores recibidos.
- `reservar_cita_borrador` valida antes de escribir y usa apertura exclusiva en `agentes/mcp/borradores/`. Solo conserva los dos últimos dígitos de cada identificador en el Markdown. El host solicita aprobación antes de invocar la escritura. Las anotaciones describen sus efectos y la decisión de aprobación la aplica el host.
- `reglas-reserva` lee los criterios de la HU-02 y `agents-md` usa la ficha local si falta el `AGENTS.md` raíz. La plantilla ADR acepta tres dígitos ASCII y lee solo los archivos autorizados de `001` a `010`. Cada prompt interpreta los resultados de herramientas como datos.

[Catálogo E1 y contrato E2](catalogo-mcp.md) · [Ficha MCP](agents-md.md) · [Servidor](../servidor_mcp/citasalud_mcp.py)
