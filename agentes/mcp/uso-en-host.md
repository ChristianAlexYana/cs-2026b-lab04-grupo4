# E5 — Uso del servidor CitaSalud en un host real

- **Responsable** · Mamani Quispe Renzo Geomar
- **Fecha de las consultas** · 23 de noviembre de 2026 (America/Lima)
- **Host** · Visual Studio Code 1.147.0, chat Local, con permisos predeterminados y sandbox activado durante la escritura.
- **Configuración** · `.vscode/mcp.json` conecta `citasalud` por stdio con el Python de `.venv`.

| N.º | Consulta en Local | Herramienta o prompt usado | ¿Pidió permiso? | Resultado |
|---|---|---|---|---|
| 1 | Usa solo cupos_disponibles de CitaSalud para Medicina General. Muestra el resultado del servidor. La consulta es de lectura. | `cupos_disponibles(especialidad="Medicina General")`. | No. | `{"especialidad":"Medicina General","disponible":true}`. Indica disponibilidad directa por especialidad. |
| 2 | Usa solo citas_del_dia de CitaSalud para consultar el 25 de noviembre de 2026. Resume el resultado sin datos personales. La consulta es de lectura. | `citas_del_dia(fecha="2026-11-25")`. | No. | `SIN_FUENTE`. El dominio carece de fecha de atención y el chat omitió el total de citas del día. |
| 3 | Usa solo validar_dni de CitaSalud con el DNI ficticio ABCDEFGH. Cita el error exacto del servidor. La consulta es de lectura. | `validar_dni(dni="ABCDEFGH")`. | No. | El servidor devolvió un error: «Error executing tool validar_dni: Usa un DNI sintético de ocho dígitos ASCII con prefijo 999.» |
| 4 (prompt MCP) | Seleccioné `/mcp.citasalud.resumen_del_dia` en las sugerencias de `/mcp.`, ingresé `2026-11-25` en el selector de fecha y envié el texto insertado. | Prompt `resumen_del_dia` y herramienta `citas_del_dia`, que el host muestra como «Consultar agenda del día». | No. | El resumen informó que la agenda del 25 de noviembre estaba indisponible porque la herramienta devolvió `SIN_FUENTE`. Omitió el total de citas. |
| 5 (escritura) | usa reservar_cita_borrador para Medicina General, con DNI ficticio 99900001 y celular ficticio 999000000 | `reservar_cita_borrador`, que el host muestra como «Crear borrador de cita». | Sí. VS Code dejó una confirmación pendiente. Después de la captura se seleccionó **Allow Once**. | Devolvió `BORRADOR-03.md`. Se comprobó que se creó un solo archivo, que los borradores previos conservaron su contenido y que el DNI y el celular se guardaron enmascarados. El archivo muestra «borrador pendiente de revisión». |

En las comprobaciones previas de las consultas 1, 2, 3 y 5 se usó el cliente Python del SDK por stdio. Para la escritura se sustituyó el DNI inicial `12345678`, que incumplía el formato de prueba, tras recibir autorización. Esa comprobación produjo `BORRADOR-02.md`. Las cinco filas de la tabla corresponden a la sesión Local de VS Code.

Al abrir el selector antes de iniciar `citasalud` en Local, `/mcp.` aparecía sin sugerencias. Después de iniciar el servidor, el selector ofreció `resumen_del_dia` y se pudo ejecutar el prompt.

## Evidencias

Las capturas se adjuntan al informe Word. La figura 3 muestra las cuatro herramientas de CitaSalud. La figura 4a muestra la confirmación antes de autorizar la escritura y la figura 4b muestra el resultado y el borrador abierto en VS Code.
