# Bitácora de IA — Lab11

## Renzo

### E1 · Catálogo MCP · 23 de noviembre de 2026

- **Consulta.** Pedí diseñar el catálogo MCP de CitaSalud a partir de `src/reservas`, las pruebas, los agentes del Lab 10 y el servidor AgroConecta del kit. Fijé las cuatro herramientas, los recursos, los prompts y el contrato de escritura del borrador.
- **Respuesta.** El asistente creó el catálogo con nueve capacidades. Identificó `ServicioReservasDespues()` y su `cupos_db` por especialidad, la `Cita` sin fecha de atención que usa el servicio y el `DniAdapter` con el SDK simulado. Propuso una salida estructurada para cupos y `SIN_FUENTE` para la agenda diaria.
- **Qué se adoptó o descartó.** Se adoptaron las firmas del catálogo y la aprobación previa del host para crear un borrador. Se descartó inferir fechas de atención a partir de eventos o fechas de registro. La consulta quedó disponible como capacidad con la limitación explícita de la fuente.
- **Verificación.** El asistente cotejó las firmas con las clases y las pruebas existentes, leyó AgroConecta como referencia y comprobó las nueve filas, las diez columnas y los enlaces del catálogo. [Catálogo](diseno/catalogo-mcp.md) · [Servicio del dominio](../../src/reservas/despues/servicio.py)

### E2 · Servidor y cliente local · 23 de noviembre de 2026

- **Consulta.** Pedí implementar el servidor y el explorador con la API del SDK instalada, verificar por stdio y ejecutar las pruebas existentes. Reservé la prueba de escritura para E5.
- **Respuesta.** El asistente implementó el servidor con `mcp==2.3.0`, adaptó el explorador y las configuraciones a CitaSalud y creó una ficha MCP para `citasalud://agents-md` porque faltaba el `AGENTS.md` raíz. Conservó las firmas y documentó que el servidor devuelve un error cuando el DNI incumple el formato sintético.
- **Qué se adoptó o descartó.** Se mantuvo el SDK del kit y se adoptó la conexión directa a CitaSalud por stdio. Se descartó usar el espía del kit para esta verificación porque su explorador borra la traza al iniciar. La aprobación humana quedó a cargo del host.
- **Verificación.** `compileall` terminó con código 0 y `pytest` pasó las 77 pruebas existentes. El explorador se verificó fuera del sandbox tras un bloqueo local con `asyncio`. Mostró el esquema y el resultado estructurado de cupos, el error de especialidad, `SIN_FUENTE`, la validación del DNI sintético, el ADR-001 y el prompt `resumen_del_dia`. [Verificación del servidor](diseno/verificacion-servidor.md)

### E5 · Pendiente de registrar

Al 23 de noviembre de 2026 quedaron documentados los argumentos de prueba para E5. La evidencia disponible corresponde a la ejecución de E2. La interacción de E5 y su verificación se registrarán cuando se realicen. [Argumentos y resultados de E2](diseno/verificacion-servidor.md)
