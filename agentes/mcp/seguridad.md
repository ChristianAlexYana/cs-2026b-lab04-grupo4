# Seguridad del servidor MCP de CitaSalud (E7)

Alcance: `agentes/mcp/servidor_mcp/citasalud_mcp.py` (propio) y `agentes/mcp/terceros/clima_mcp.py` (servidor ficticio de terceros del laboratorio, que solo se audita y no se conecta a ningún host). Todo el trabajo usa datos sintéticos.

## Auditoría con `cliente/auditar.py`
Comandos: `python agentes/mcp/cliente/auditar.py agentes/mcp/servidor_mcp/citasalud_mcp.py` y lo mismo con `agentes/mcp/terceros/clima_mcp.py`. El código de salida es 1 si hay hallazgos de severidad ALTA.

**Servidor propio** (salida 0, sin hallazgos ALTA):
```
Servidor: citasalud
  [BAJA ] cupos_disponibles      texto libre sin límite en el esquema: especialidad
  [BAJA ] citas_del_dia          texto libre sin límite en el esquema: fecha
  [BAJA ] validar_dni            texto libre sin límite en el esquema: dni
  [BAJA ] reservar_cita_borrador texto libre sin límite en el esquema: celular, dni, especialidad
```
**Servidor de terceros** (salida 1):
```
Servidor: clima-majes
  [ALTA ] clima_majes            instrucciones ocultas dirigidas al modelo
  [ALTA ] clima_majes            pide secretos o credenciales
  [MEDIA] clima_majes            pide leer datos ajenos a su función
  [MEDIA] clima_majes            parámetro genérico 'contexto' que podría usarse para filtrar datos
  [BAJA ] clima_majes            sin anotaciones (¿solo lectura? ¿destructiva?)
  [BAJA ] clima_majes            texto libre sin límite en el esquema: contexto
```
La herramienta del servidor de terceros parece un pronóstico del clima, pero su descripción ordena al modelo leer el `.env` y un recurso del proyecto, copiarlos en el parámetro `contexto` y no avisar al usuario: envenenamiento de herramientas. Por eso no se conecta a un host.

## Reglas nuevas del auditor (probadas en `agentes/mcp/pruebas/test_auditor.py`)
1. **Escritura sin `destructiveHint` explícito** (MEDIA): si la herramienta no declara `readOnlyHint=true` ni `destructiveHint`, el protocolo la trata como destructiva por defecto. Nuestra escritura declara `destructive_hint=False`, por eso no dispara.
2. **Texto libre sin límite en el esquema** (BAJA): parámetros `string` sin `maxLength`, `enum`, `pattern` ni `const`. Dispara en los cuatro tools del servidor propio.

Hallazgo sobre el servidor propio: los cuatro parámetros de texto se validan en el código con expresiones regulares y claves exactas, pero el esquema que ve el modelo no declara esos límites. Decisión: aceptarlo y documentarlo; declarar `pattern` o `maxLength` en el esquema es la mejora pendiente y haría crecer el catálogo (ver `protocolo.md`).

## Lista de verificación
| Control | Evidencia | Estado |
|---|---|---|
| Mínimo privilegio | Tres herramientas son de solo lectura (`read_only_hint=True`); una sola escritura, `reservar_cita_borrador`, que solo crea archivos nuevos con modo exclusivo (`archivo.open("x")`) y no reserva cupo ni envía mensajes. Sin shell, red ni lectura de archivos arbitrarios (`open_world_hint=False`). Prueba: `test_minimo_privilegio_una_sola_herramienta_de_escritura`. | Cumple |
| Validación de entradas | DNI `999[0-9]{5}`, celular `999[0-9]{6}`, fecha `AAAA-MM-DD` de calendario, especialidad por clave exacta, ADR de tres dígitos ASCII, `redactar_criterios` con id ≤ 64 y historia ≤ 4000 caracteres. Pruebas: `test_validar_dni_rechaza_formatos_no_sinteticos`, `test_borrador_rechaza_entradas_invalidas_sin_crear_nada`, `test_propia_celular_con_digitos_de_ancho_completo_se_rechaza`. | Cumple en el código; el esquema no lo declara (regla 2) |
| Rutas seguras en recursos | Los ADR salen de una lista blanca (`ADR_AUTORIZADOS`, 001 a 010), sin armar rutas con texto del usuario; `_leer_documento` rechaza enlaces simbólicos y la carpeta de borradores se comprueba con `resolve()`. Prueba: `test_recurso_plantilla_adr_y_validacion` (`..%2F..%2Fsecretos`, `abc`, `999`). | Cumple; el rechazo de enlaces simbólicos no tiene prueba propia |
| Ausencia de secretos | Sin claves en el código ni en las configuraciones de `agentes/mcp/config/`. Búsqueda `grep -rniE "api_key\|secret\|token\|password\|passwd\|bearer"` sobre `agentes/mcp` (`.py`, `.json`, `.md`, `.txt`): solo aparecen las palabras «tokens» (en `costo_catalogo.py`) y «secretos» (en dos pruebas) y el servidor de terceros; ninguna credencial. | Cumple |
| Aprobación de la escritura | En el agente: `Politica.requieren_aprobacion` con `aprobar_en_consola` (solo `s` o `n`); prueba `test_adaptador_descubre_y_ejecuta_y_la_politica_exige_aprobacion`. En el host: VS Code pidió confirmación y se eligió *Allow Once* (`uso-en-host.md`, consulta 5). Las instrucciones del servidor también la exigen. | Cumple |
| Datos de pacientes | Solo datos sintéticos; los borradores guardan el DNI y el celular enmascarados. | Cumple |

## Limitaciones
- Las anotaciones (`readOnlyHint`, `destructiveHint`) son pistas del servidor, no garantías (guía, Tabla 6; el propio SDK lo advierte). La política del agente exige aprobación a lo que no declara `read_only_hint`, así que depende de que el servidor no mienta. Con servidores de terceros hay que auditar el catálogo y no confiar en esas pistas.
- El transporte es stdio local, sin autenticación; no se probó Streamable HTTP ni OAuth.
- La auditoría revisa descripciones y esquemas con reglas simples; no detecta un servidor que cambie su catálogo después de la revisión.
