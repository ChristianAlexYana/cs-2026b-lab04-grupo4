# ADR-011: Exponer CitaSalud mediante un servidor MCP
Estado: Aceptado
Fecha: 2026-11-27
Decisores: Equipo 04 (Sergio, Christian, Renzo)

## Contexto
En el Laboratorio 10 las herramientas del agente (leer archivos, ejecutar pruebas, editar) estaban escritas dentro de su propio código. Cualquier otro host (VS Code con Copilot, Claude Code, Gemini CLI) necesitaría su propio adaptador: con N hosts y M fuentes, N × M integraciones. El proyecto maneja datos personales de pacientes (Ley 29733), así que lo que se publique debe ser mínimo, auditable y probado sin un modelo.

## Alternativas consideradas
1. **API REST directa** que cada host consuma con su propio adaptador. Descartada: no hay descubrimiento estándar de capacidades, cada host necesita su cliente y su descripción para el modelo, y volvería el problema N × M.
2. **Function calling dentro del agente** (lo que hacía el Lab 10). Descartada: las herramientas quedan atadas a un solo agente y a un solo proveedor, y no se pueden auditar ni reutilizar por separado.
3. **Servidor MCP** que publique el sistema una vez y lo descubran los hosts (N + M). Elegida.

## Decisión
Usaremos un servidor MCP, `agentes/mcp/servidor_mcp/citasalud_mcp.py`, con el SDK `mcp==2.3.0` (`agentes/mcp/requirements.txt`), transporte **stdio** y versión del protocolo **2026-07-28** (confirmada en el tráfico de `consulta1`).

**Qué se expone**
- Herramientas: `cupos_disponibles`, `citas_del_dia` y `validar_dni` (solo lectura) y `reservar_cita_borrador` (la única escritura).
- Recursos: `citasalud://reglas-reserva`, `citasalud://agents-md` y la plantilla `citasalud://adr/{numero}` (ADR 001 a 010).
- Prompts: `resumen_del_dia` y `redactar_criterios`.

**Qué no se expone**: la reserva real del cupo ni los eventos de WhatsApp (la escritura solo crea un borrador), datos reales de pacientes o del RENIEC, archivos arbitrarios, shell y red. `citas_del_dia` devuelve `SIN_FUENTE` porque el dominio no tiene una agenda de atención consultable.

**Controles de seguridad**
- Mínimo privilegio: una sola escritura, que solo crea archivos nuevos (`open("x")`) en `agentes/mcp/borradores/`, con DNI y celular enmascarados.
- Validación de entradas en el servidor (DNI y celular sintéticos, fecha de calendario, especialidad exacta) y errores que explican cómo corregir.
- Recursos por lista blanca de ADR y sin enlaces simbólicos.
- Aprobación humana de la escritura, en el host (*Allow Once* en VS Code) y en el agente (`Politica.requieren_aprobacion`).
- Anotaciones declaradas (`readOnlyHint`, `destructiveHint=false`), tratadas como pistas y no como garantías.
- Auditoría antes de conectar un servidor ajeno (`cliente/auditar.py`, con dos reglas propias); el servidor de terceros del laboratorio solo se audita.
- Pruebas de contrato sin LLM (`agentes/mcp/pruebas/`, 36 pruebas) y trazas JSON-RPC (`cliente/espia.py`).

## Consecuencias
Positivas: cualquier host compatible descubre las mismas capacidades; el agente del Lab 10 usa el servidor sin cambiar su núcleo; el servidor se prueba y se audita por separado; una consulta típica costó 14 mensajes y 7 201 bytes, y el catálogo pesa 1 975 caracteres (unos 493 tokens) por turno.
Negativas / riesgos: las anotaciones dependen de que el servidor sea honesto; stdio es solo local y sin autenticación (no se implementó Streamable HTTP ni OAuth); el esquema no declara los límites de los parámetros de texto, que solo se validan en el código (cuatro hallazgos BAJA del auditor); `citas_del_dia` no entrega datos hasta que el dominio tenga una agenda; la evidencia es pequeña (una consulta del agente y cinco de un host).
