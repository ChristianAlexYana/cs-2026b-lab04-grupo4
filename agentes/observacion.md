# Observación de las corridas de Renzo (E4 y E5)

Las decisiones se registraron con `ModeloInteractivo`; cada herramienta operó sobre
`agentes/trabajo/`, una copia nueva por corrida. El cambio aplicado a `src/` se
revisó con `git diff --no-index` antes de copiarlo. Ningún ejecutor editó `tests/`.

| Corrida | Rondas | Acciones permitidas | Bloqueadas | Contrato inválido | Contexto final |
| --- | ---: | ---: | ---: | ---: | ---: |
| E2, issue 1, único (referencia de Christian) | 1 | 8 | 1 | 0 | 17 675 caracteres |
| E4, issue 3, único con mapa y notas | 1 | 9 | 0 | 0 | 16 164 caracteres |
| E5, issue 2, único | 1 | 5 | 0 | 0 | 4 381 caracteres |
| E5, issue 2, actor–crítico | 1 | 6 | 0 | 0 | 7 613 caracteres entre tres agentes |

El contexto E2 y E4 es el recuento de `str(historial)` impreso por el runner;
el de E5 usa `json.dumps(historial, ensure_ascii=False)` para comparar las dos
variantes con la misma medida. En E5 el actor–crítico se descompone en
planificador (935), ejecutor (4 953) y revisor (1 725) caracteres. La memoria
de E4 guardó una nota de 109 bytes dentro del sandbox y se recuperó una vez.
E4 no redujo los pasos frente a E2 (9 frente a 9); el contexto fue 1 511
caracteres menor, pero son issues distintos, por lo que no se puede atribuir
esa diferencia a las notas. La primera edición del issue 3 causó una regresión
en una cita simulada sin atributo `estado`; las pruebas la detectaron y el
agente la corrigió en una segunda edición.

## Comparación de coordinación para el issue 2

El agente único modificó `ReniecSDK.consultar` con `dni.isdigit()` y dejó las
54 pruebas de la copia en verde. El planificador del actor–crítico pidió revisar
también los dígitos Unicode; el ejecutor validó ocho dígitos ASCII en
`DniAdapter` y el revisor comprobó el diff y la suite. Aprobó en la primera
ronda y no pidió cambios. Una prueba de regresión añadida por el humano confirma
la diferencia: `"１２３４５６７８".isdigit()` es verdadero y esa entrada debe rechazarse.
Con el cambio aprobado aplicado al repositorio, `pytest -q` da 74 aprobadas
(incluida una prueba adicional de la política).

El bucle actor–crítico agregó una acción (6 frente a 5) y 3 232 caracteres de
contexto (7 613 frente a 4 381). En esta corrida, el planificador identificó
un caso que la variante única pasó por alto, pero el revisor no encontró un
defecto adicional ni fue necesaria una segunda ronda. Para un error tan
acotado, el costo de tres agentes no se justifica de forma general: conviene
empezar con uno y agregar revisión independiente cuando el riesgo o la
complejidad del cambio lo requieran (principio de parsimonia).

## Interacciones registradas para la bitácora de E7

| Corrida y paso | Decisión u observación | Efecto |
| --- | --- | --- |
| E4, paso 1 | `ejecutar_pruebas` encontró cuatro fallos | Se reprodujo el issue 3 antes de editar. |
| E4, pasos 2–4 | `mapa_repo`, `anotar` y `leer_archivo` ubicaron el suscriptor | La nota quedó en `trazas/issue3_notas/notas.md`. |
| E4, pasos 6–8 | Las pruebas detectaron `AttributeError` tras la primera edición | El ejecutor corrigió el acceso a `estado` y repitió pytest. |
| E5 único, paso 4 | `editar_archivo` añadió `isdigit()` al SDK | Las pruebas existentes pasaron, pero quedó el caso Unicode. |
| E5 actor–crítico, plan | El planificador incluyó los dígitos Unicode | El ejecutor aplicó validación ASCII en el adaptador. |
| E5 actor–crítico, revisor | `ver_cambios` y `ejecutar_pruebas` verificaron el cambio | Primera ronda aprobada; cero acciones bloqueadas. |

Trazas y diagramas: `trazas/issue3_notas/`, `trazas/issue2_unico/` y
`trazas/issue2_actor_critico/`. Las decisiones completas están en
`trayectorias/` con las mismas etiquetas.
