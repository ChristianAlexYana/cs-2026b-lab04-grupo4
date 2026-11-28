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

### E5 · Uso de CitaSalud en VS Code · 23 de noviembre de 2026

| Consulta | Respuesta observada | Decisión y verificación |
|---|---|---|
| Consultar disponibilidad de Medicina General. | `cupos_disponibles` devolvió `disponible: true`. | Se aceptó como disponibilidad actual por especialidad. Se verificó la llamada a CitaSalud y el resultado en el chat Local. |
| Consultar las citas del 25 de noviembre de 2026. | `citas_del_dia` devolvió `SIN_FUENTE`. | Se informó que la agenda está indisponible. El chat omitió el total de citas y mostró la llamada en sus pasos. |
| Validar el DNI de prueba `ABCDEFGH`. | `validar_dni` devolvió un error que pide ocho dígitos ASCII con prefijo `999`. | Se registró el mensaje exacto del servidor y se comprobó el mismo rechazo en Local. |
| Ejecutar `resumen_del_dia` desde el selector de prompts MCP. | Con `fecha=2026-11-25`, el prompt llamó a `citas_del_dia` y el chat resumió `SIN_FUENTE`. | Las sugerencias aparecieron después de iniciar CitaSalud en Local. Se seleccionó la sugerencia real y se comprobó la herramienta que figuraba en los pasos de VS Code. |
| Crear un borrador de Medicina General con datos de prueba. | El DNI inicial quedaba fuera del formato admitido. Con el DNI de prueba aprobado, la llamada en Local devolvió `BORRADOR-03.md`. | Se verificó la confirmación del host y se autorizó con **Allow Once**. La terminal mostró un único archivo nuevo. En VS Code se comprobó el enmascaramiento y el estado de borrador pendiente de revisión. |

Las capturas de descubrimiento, permiso y resultado se adjuntan al informe Word. [Registro de las cinco consultas](uso-en-host.md)

## Christian

Registrado según su traspaso del 25 de noviembre de 2026.

### E3 · Pruebas de contrato e Inspector · 25 de noviembre de 2026

- **Consulta.** Pedí adaptar las pruebas del kit al servidor entregado y abrirlo en MCP Inspector.
- **Respuesta.** El asistente propuso las pruebas del kit tal cual. Contra el servidor real fallaron 13 de las 25 por diferencias de formato. La ruta con `\` que usé para abrir el Inspector no funcionó, porque el Inspector consumió las barras.
- **Qué se adoptó o descartó.** Se adaptaron las pruebas al servidor real, no al revés. La ruta se corrigió con `/`.
- **Verificación.** `python -m pytest -q agentes\mcp\pruebas` terminó con 25 pruebas en verde.

### E4 · Política con aprobación de escritura · 25 de noviembre de 2026

- **Consulta.** Pedí copiar la política del kit para exigir aprobación a la herramienta de escritura.
- **Respuesta.** La política del repositorio no tenía `requieren_aprobacion`. Se comparó con la del kit antes de copiarla.
- **Qué se adoptó o descartó.** Se agregaron solo cuatro líneas (el conjunto, la función `aprobar` y un `if` final), compatibles hacia atrás con el Lab 10.
- **Verificación.** La suite general siguió en 77 pruebas en verde.

## Sergio

### E6 · Verificación de la traza y del script · 27 de noviembre de 2026

- **Consulta.** Pedí revisar el repositorio, las notas de Christian y preparar E6, E7 y E8.
- **Respuesta.** El asistente recalculó las métricas de `consulta1` con `traza_mcp.cargar` y `metricas`, y coincidieron con las notas: 14 mensajes, 1 error, 7 201 bytes y 16 flechas en el diagrama. También confirmó que el bloque `__main__` de `traza_mcp.py` ignoraba el argumento.
- **Qué se adoptó o descartó.** Su primera corrección escribía el diagrama como `mcp_trafico.mmd` y creaba un archivo duplicado junto al `trafico.mmd` existente. Lo vimos en `git status`; se cambió para que la salida sea `trafico.mmd` en la misma carpeta de la traza.
- **Verificación.** Se volvió a ejecutar el script sobre `consulta1`: mismas cifras y un solo `.mmd`.

### E6 · Optimización del catálogo · 27 de noviembre de 2026

- **Consulta.** Pedí optimizar el catálogo y medir el efecto.
- **Respuesta.** El asistente midió 2 009 caracteres (≈ 502 tokens) y propuso quitar los `title` y fusionar `validar_dni` con la escritura.
- **Qué se adoptó o descartó.** Se descartó quitar los `title` porque el host los muestra y están en la evidencia de `uso-en-host.md`, y se descartó la fusión porque rompía pruebas y evidencias de E4 y E5. Se acortaron las descripciones: 1 975 caracteres (−1,7 %).
- **Verificación.** Las 25 pruebas del servidor siguieron en verde y la repetición de `consulta1` dio los mismos 6 pasos.

### E7 · Servidor de terceros ausente · 27 de noviembre de 2026

- **Consulta.** Pedí auditar `terceros/clima_mcp.py`.
- **Respuesta.** El archivo no estaba en el repositorio (`main` no tenía la carpeta `terceros`). El asistente lo copió sin cambios desde el zip de recursos del docente.
- **Qué se adoptó o descartó.** Se adoptó el archivo original, sin adaptarlo, para auditar el mismo servidor que entregó el docente.
- **Verificación.** El auditor lo marcó con dos hallazgos ALTA y salió con código 1.

### E7 · Reglas nuevas del auditor · 27 de noviembre de 2026

- **Consulta.** Pedí dos reglas nuevas con pruebas.
- **Respuesta.** El asistente separó la revisión por herramienta en una función (`hallazgos_de`) y agregó escritura sin `destructiveHint` y texto libre sin límite en el esquema. Las pruebas usan herramientas sintéticas y los dos servidores reales.
- **Qué se adoptó o descartó.** La regla de texto libre disparó cuatro hallazgos BAJA en el servidor propio, que no tenía esperados. Se aceptaron y se documentaron en `seguridad.md` en lugar de agregar `pattern` al esquema, que haría crecer el catálogo.
- **Verificación.** 36 pruebas del servidor en verde (25 anteriores y 11 nuevas).

