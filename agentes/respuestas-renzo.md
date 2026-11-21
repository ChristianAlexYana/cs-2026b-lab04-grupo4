# Respuestas de Renzo para el informe del Lab 10

## 2. Arquetipos para los tres issues

Usaría ReAct como agente único para el issue 1 (cupo duplicado) y el issue 3
(recordatorio a cita cancelada): ambos requieren leer código, proponer una
edición pequeña y comprobarla con pruebas. Para el issue 2 (DNI) comparé ese
arquetipo con planificador–ejecutor y actor–crítico. La segunda variante
separó el plan, la edición y una revisión de solo lectura porque validar una
identidad exige mirar también los casos límite que la suite inicial omite.

## 5. Memoria de E4

La memoria de corto plazo es el historial de decisiones y observaciones de la
corrida. Añadí notas persistentes solo durante esa corrida mediante `anotar` y
`leer_notas`: el agente guardó la ruta de `NotificadorWhatsApp.actualizar` en
`notas.md` dentro de la copia aislada y la recuperó una vez. E4 usó nueve
acciones, igual que la referencia E2; su contexto final fue de 16 164
caracteres frente a 17 675 en E2. Son problemas distintos, así que la
diferencia de 1 511 caracteres no prueba que la memoria ahorre contexto.

## 6. Costo del actor–crítico y parsimonia

Para el issue 2, el agente único hizo cinco acciones y consumió 4 381
caracteres de contexto. El conjunto planificador–ejecutor–revisor hizo seis
acciones y consumió 7 613 caracteres. El planificador planteó el caso de los
dígitos Unicode que la variante única no había cubierto; el ejecutor lo
resolvió con una validación ASCII en el adaptador. El revisor aprobó en la
primera ronda y no encontró otro defecto. El beneficio de esta corrida fue
un caso límite adicional, con más costo. Por parsimonia, mantendría un agente
único para fallos simples y reservaría la revisión independiente para cambios
de mayor riesgo.
