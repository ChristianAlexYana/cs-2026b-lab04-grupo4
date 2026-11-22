# Bitácora de interacciones con el asistente (Lab 10)

Registro de las interacciones del Laboratorio 10: el asistente decide y el humano pega la decisión en `ModeloInteractivo`. Las decisiones completas están en `agentes/trayectorias/<corrida>/` y las trazas en `agentes/trazas/<corrida>/`. La bitácora general del proyecto sigue en `docs/architecture/bitacora-ia.md`.

| # | Corrida | Qué propuso el asistente | Qué detectamos | Quién lo detectó | Decisión |
|---|---|---|---|---|---|
| 1 | Issue 1, antes de empezar | Tres respuestas con comillas tipográficas (`“ ”`) en lugar de `" "` | No son JSON válido y habrían tumbado la corrida. | Nosotros, antes de pegarlas en la consola | Se pidió al asistente repetir la decisión dentro de un bloque de código. No se corrigió nada a mano. |
| 2 | Issue 1, paso 5 | Editó `servicio.py` sin haber corrido `ejecutar_pruebas` en rojo antes | La reproducción del error se hizo después; las pruebas del paso 6 confirmaron el cambio. | Nosotros, al leer la traza | Aceptada; anotado como mala práctica del agente. |
| 3 | Issue 1, paso 8 | Pidió `ver_cambios` para revisar su propia edición | El contrato la aceptó (está en el catálogo) pero la política del ejecutor no la permite. | La política (`BLOQUEADO`) | Se mantuvo el bloqueo: mínimo privilegio. El agente leyó el archivo en su lugar. |
| 4 | Issue 3, pasos 6 a 8 | Primera edición de `eventos.py` leyendo `cita.estado` | `AttributeError` en una cita simulada sin atributo `estado`. | Las pruebas (`ejecutar_pruebas`) | El agente corrigió el acceso en una segunda edición y repitió pytest. |
| 5 | Issue 2, agente único, paso 4 | Agregó `dni.isdigit()` en `ReniecSDK.consultar` | Las pruebas existentes pasaron, pero `"１２３４５６７８".isdigit()` es verdadero: un DNI con dígitos Unicode seguiría aceptándose. | El planificador del actor-crítico, en la otra variante; luego una prueba de regresión añadida por el humano | El cambio aprobado se aplicó con validación de ocho dígitos ASCII. |
| 6 | Issue 1, repetición con aprobación (`issue1_aprobacion`) | Misma edición del paso 5, ahora con `--aprobar` | Se mostró el diff y se respondió «s»: pasó. | El humano (E6) | Aceptada. |
| 7 | Issue 1, repetición con rechazo (`issue1_rechazo`) | Misma edición del paso 5 | Se respondió «n»: la política devolvió `El revisor humano rechazó la edición`; el agente siguió con las demás decisiones grabadas. | El humano y la política (E6) | Bloqueo confirmado. Es una repetición, no un asistente en vivo. |

Todas las entradas salen de trazas y trayectorias reales del repositorio; la 6 y la 7 se reproducen con los comandos de `agentes/delegacion.md`. No se incluyó información personal ni credenciales.
