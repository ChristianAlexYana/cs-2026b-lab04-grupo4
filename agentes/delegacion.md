# Delegación progresiva del agente de CitaSalud (E6)

El rol humano pasa de ejecutor a gobernador (Albada, 2025, cap. 13; guía, sección 1.8, Figura 6). Hoy el agente está en **revisor**: actúa sobre una copia (`agentes/trabajo/`) y una persona aprueba cada edición con `--aprobar`, aplica el cambio al repositorio, corre pytest y hace el commit. Los datos de abajo salen de las trazas de `agentes/trazas/`: cuatro corridas de agente único o actor-crítico sobre los tres issues, más una repetición con aprobación humana (`issue1_aprobacion` y `issue1_rechazo`).

| Rol humano | Qué hace la persona | Qué puede hacer el agente de CitaSalud | Evidencia que justifica pasar al siguiente |
|---|---|---|---|
| Ejecutor | Hace el trabajo; el agente solo sugiere. | `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`, `leer_notas`. Ninguna escritura. | Que el agente ubique el archivo y el error correctos en los tres issues. En las trazas lo hizo: leyó `servicio.py`, `externos.py` y `eventos.py` antes de proponer cualquier cambio. |
| **Revisor (hoy)** | Aprueba o rechaza cada edición y aplica el cambio al repo. | Lo anterior más `editar_archivo` (solo en la copia de trabajo, nunca en `tests/`), `ejecutar_pruebas` y `ejecutar_comando` limitado a pytest, radon, lint-imports y `git status`/`git diff`. Máximo de 15 pasos. | Los tres issues se resolvieron y las pruebas quedaron en verde. Hubo 0 decisiones rechazadas por el contrato y 0 ediciones en `tests/`. La política bloqueó `ver_cambios` en el issue 1, que el ejecutor no tiene permitida. |
| Colaborador | Define el objetivo y revisa el resultado; aprueba solo los cambios de riesgo (datos personales, concurrencia). | Editar y correr pruebas sin pedir permiso en cambios acotados (un archivo, sin tocar `src/reservas/externos.py` ni la reserva de cupos). Edición de archivos nuevos solo con revisor independiente. | Faltan datos: cuatro corridas y tres issues no alcanzan. Habría que pedir, por ejemplo, 10 issues más de dificultad parecida, todos resueltos sin que el humano rechazara una edición por incorrecta, y ver si el revisor encuentra algo que el agente único pasó por alto (en el issue 2 no encontró nada extra). |
| Gobernador | Fija reglas, límites y presupuesto; audita las trazas por muestreo. | Trabaja con el flujo completo (planificar, editar, probar, abrir un Pull Request) y la persona revisa por muestreo. Aun así no fusiona su propio cambio. | Meses de trazas sin incidentes, pruebas de inyección indirecta y de exceso de agencia (Laboratorio 13) y control del costo por tarea. No lo tenemos y no lo pedimos para este laboratorio. |

## Cómo está activa la aprobación

`aprobar_edicion` está en la política del ejecutor (`agentes/agente/politica.py`) y se activa con `--aprobar` (`politica_ejecutor` en `agentes/comun.py`). Antes de cada `editar_archivo` la consola muestra el fragmento actual y el nuevo, y espera «s» o «n»: cualquier otra respuesta se vuelve a pedir (Tabla 8, validar la entrada humana). Si la respuesta es «n», el agente recibe la observación `BLOQUEADO POR LA POLÍTICA: El revisor humano rechazó la edición` y decide de nuevo.

Pruebas en `agentes/pruebas_agente/test_agente.py`:
`test_aprobacion_humana_rechazada_bloquea_la_edicion`, `test_aprobacion_humana_no_se_pide_para_lecturas` y `test_consola_solo_acepta_s_o_n`.

## Qué no demuestra la evidencia

- La aprobación se probó con una **repetición** de la trayectoria grabada del issue 1 (`--modelo grabado`): las decisiones del asistente no cambian cuando la persona rechaza. Muestra que el bloqueo funciona, no cómo reaccionaría un asistente en vivo.
- En ambas repeticiones se respondió «s» o «n» sin discusión previa del diff real; en `issue1_unico` el arreglo se aplicó después de revisar el diff de la copia de trabajo.
- Los criterios de la fila «Colaborador» son una propuesta del equipo, no una regla de la guía.
