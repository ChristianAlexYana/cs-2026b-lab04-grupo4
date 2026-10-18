# Bitácora de IA — Laboratorio 06 · CitaSalud Arequipa

Regla de oro: la IA propone, el equipo decide y verifica.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 17/10/2026 | Claude | Prompt IA 2 (auditor C4): revisar las 5 vistas exportadas con la lista de c4model.com, en tabla con vista, pregunta, cumple sí/no, evidencia y corrección | Tabla con 5 hallazgos: personas sin protocolo en el nivel 1, externos sin distinguir en PlantUML, Nginx suelto en despliegue, "ciclo" Reservas–Notificaciones y que todas tienen título y leyenda | Se contrastó cada hallazgo con las imágenes de `img/` y con `workspace.dsl`. Dos eran falsos positivos (personas sin protocolo; ciclo que no existe, solo hay Reservas → Notificaciones) | Corregida: 3 aceptados, 2 rechazados |
| 2 | 17/10/2026 | Claude | Validar `workspace.dsl` con Structurizr CLI y revisar el contenido de los .puml exportados | Confirmó que el modelo valida sin errores y que el export PlantUML usa `System` también para los externos (`$tags=""`) | Se comprobó en el .puml y en el PNG: es cierto. La etiqueta `Externo` solo se ve en Mermaid y Structurizr Lite | Aceptada: limitación documentada en revision-c4.md |
| 3 | 17/10/2026 | Claude | Prompt IA 3: explicar el contexto a una persona no técnica en 120 palabras o menos | Revisó el texto de `explicacion.md` (86 palabras) | Se contaron las palabras con un script y se verificó cada afirmación: reservar/cancelar y ver horarios (Paciente → CitaSalud), recordatorio por WhatsApp, consulta de DNI y reintentos del Worker (ADR-003) | Aceptada |
| 4 | 17/10/2026 | Claude | Armar la sección "Arquitectura C4 (Lab 06)" del README con el contexto en Mermaid | Sección con el contenido de `export/structurizr-Contexto.mmd` y enlaces a las 5 imágenes | Se verificó que el bloque Mermaid es idéntico al export y que los 5 PNG existen en `img/` | Aceptada |


> No se incluyó información personal ni confidencial en ningún prompt.
