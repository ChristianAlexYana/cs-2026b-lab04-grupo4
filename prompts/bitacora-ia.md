# Bitácora de IA — Lab 09 (Bloque 3)

Solo se registran interacciones de este bloque. Las grabaciones de E2 a E4 son simuladas (no vienen de un LLM en vivo).

| # | Herramienta | Qué se pidió | Qué propuso | Qué se verificó | Decisión |
|---|---|---|---|---|---|
| 1 | Claude | Preparar el CI de prompts | Usar `PROMPTFOO_FAILED_TEST_EXIT_CODE=0` porque promptfoo sale con código 100 si falla algún caso | Se ejecutó promptfoo en un contenedor: v1 fallaba y salía con 100; con la variable salía 0 | Aceptada |
| 2 | Claude | Dependencias de E6 en CI | Agregar `jsonschema` a los `pip install` | Sin `jsonschema` las pruebas del generador no importan el módulo | Aceptada |
| 3 | Claude | Fechas de la Tarea B caducan (ventana de 30 días) | Variable `FECHA_REFERENCIA` (2026-11-14, día de la grabación) que usa la aserción B6; sin la variable usa la fecha de hoy | Se reejecutó la Tarea B con la variable: v1 0/8, v2 3/8, v3 7/8, igual que la ejecución de Renzo | Aceptada |
| 4 | Claude | Generador de datos de prueba (E6) | Validar con el esquema y con guardrails de ficción e integridad (ids únicos, citas con paciente existente, totales) | `pytest`: B1 de v3 se acepta, B8 de v3 se rechaza por DNI de 8 dígitos, y 3 casos más; 49 pruebas en verde y `lint-imports` con 2 contratos cumplidos | Aceptada |
| 5 | Claude | Resumen de la lista de verificación del Paso 9 en el contexto del grupo | Un resumen de memoria de esa lista | No estaba en el material leído; la lista se quitó y se remitió a la guía | Rechazada |
| 6 | Claude | Compuerta de calidad del workflow | Comprobar tasas exactas esperadas por versión en `resultados.json` y fallar solo ante regresión | Las tasas reales de Renzo coinciden: A 0/8, 3/8, 7/8, 8/8; B 0/8, 3/8, 7/8 | Aceptada |

## No determinismo
Con el proveedor grabado, las tres ejecuciones de H1, H5 y H8 (tarea A) dieron resultados idénticos, como era de esperar: lee siempre el mismo archivo. No se observó variación y no se afirma. Para medirla hace falta un proveedor real con autorización y temperatura 0.
