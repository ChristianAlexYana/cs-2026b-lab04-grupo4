# Bitácora de uso de IA — CitaSalud Arequipa

> **Nota del grupo:** todas las entradas corresponden a interacciones con Claude durante el laboratorio. Las entradas 1 y 2 documentan la evaluación de alternativas arquitectónicas (E2); las entradas 3 a 8 registran la generación de los demás entregables, con nuestras verificaciones y correcciones para garantizar el cumplimiento de las restricciones del proyecto.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 30/09 | Claude | Prompt 1 (E2): 3 alternativas de estilo para CitaSalud con plazo de 1 mes y equipo de 3 | Propuso Monolito en Capas, Monolito Modular y Microservicios. Recomendó Microservicios argumentando que era la única forma de soportar los 5000 usuarios recurrentes. | La afirmación de que Microservicios es indispensable es exagerada. Verificamos que para un equipo de 3 personas y un plazo de 1 mes, la sobrecarga de operar múltiples despliegues y bases de datos rompe las restricciones R-01 y R-02. | Rechazada (se eligió Monolito Modular) |
| 2 | 30/09 | Claude | Prompt 2 (E2): crítica adversarial a la alternativa de Microservicios | Enumeró 5 riesgos: complejidad de despliegue, latencia de red, consistencia eventual de datos, sobrecarga operativa y costo de infraestructura (requiere Kubernetes/varios nodos). | Verificamos que los riesgos aplican directamente a nuestras restricciones (R-03: un solo VPS de bajo costo) y al QA-02 (riesgo de citas duplicadas por consistencia eventual). Esto confirmó nuestra decisión de descartarlo. | Aceptada |
| 3 | 30/09 | Claude | Se subió la guía del laboratorio y se eligió el caso CitaSalud; se pidió armar `drivers.md` (E1) | 7 requisitos funcionales, 5 atributos de calidad, 5 restricciones y 3 escenarios (QA-01 p95 ≤ 3 s; QA-02 0 cupos duplicados en 10 000 intentos; QA-03 100 % de 50 accesos indebidos denegados) | Se corrigió R-02 con las tecnologías reales del grupo, tal como figuran en `drivers.md`. Se cuestionó el "cálculo de referencia": se aclaró que es una estimación (5000 ÷ 900 s ≈ 5,6 reservas/s) y que el supuesto de "8 peticiones por sesión" se justifica con el flujo real. | Corregida |
| 4 | 30/09 | Claude | Generar `matriz-decision.md`: 3 alternativas, 6 criterios con pesos y puntajes | Matriz con monolito en capas, monolito modular y microservicios. El primer cálculo dio empate (4,25 y 4,25); la IA reajustó los pesos y quedó modular 4,20, capas 4,10, microservicios 2,75 | Reconocimos que ajustar pesos para obtener un ganador es un sesgo. Por eso comprobamos que cada peso final se justifique con un driver (ver `matriz-decision.md`) y recalculamos a mano cada total Σ(peso × puntaje): 4,20 / 4,10 / 2,75. | Corregida |
| 5 | 30/09 | Claude | Generar `arquitectura.mmd` a partir de la matriz | Diagrama Mermaid con 3 actores, 5 módulos, PostgreSQL, Redis y WhatsApp | Al validar en mermaid.live apareció primero un diagrama distinto porque el editor conservaba código anterior; se limpió el editor y se comprobó el diagrama correcto. Se revisó que cada módulo cubra al menos un RF de `drivers.md`. | Aceptada |
| 6 | 30/09 | Claude | Generar `alternativa.puml` de la segunda mejor alternativa (capas, 4,10) | Diagrama PlantUML de componentes con nota de 4 líneas que cita el puntaje | Al revisar la imagen de plantuml.com se vio PostgreSQL fuera del servidor, lo que contradice la vista de despliegue (un solo VPS, R-03). Se movió la base de datos dentro del nodo, se regeneró la imagen y se subió al repositorio mediante un Pull Request revisado por otro integrante. | Corregida |
| 7 | 30/09 | Claude | Generar `despliegue.py` (E6) con Python Diagrams | Primera versión casi idéntica al ejemplo del docente; luego se agregaron Gunicorn y Prometheus para diferenciarla | El grupo detectó que Gunicorn, Prometheus y Grafana no figuraban en ninguna decisión ni ADR. Se eliminaron Gunicorn y Prometheus; el monitoreo quedó rotulado "herramienta por definir" y el ícono de Grafana se mantiene solo como representación genérica. Los diagramas deben ser coherentes con los ADR. | Corregida |
| 8 | 30/09 | Claude | Redactar ADR-004 de stack tecnológico y revisar ADR-002 | Django + DRF y React/Angular (PWA). En el ADR-002 afirmó que MySQL no tiene índices parciales nativos | Verificamos en la documentación oficial de MySQL (`CREATE INDEX` y columnas generadas) que no hay índices parciales nativos y que sí se puede usar `UNIQUE` sobre columnas generadas. En Django, `UniqueConstraint(condition=...)` existe [3]. Con eso se completó el ADR-002 con las referencias [1]–[3] y se retiró el marcador "[Verificar…]". Confirmamos PostgreSQL y el stack definido en el ADR-004. | Corregida |

## Anexo: prompts

**Prompt 1 (entrada 1)**
```
Actúa como arquitecto de software senior con experiencia en sistemas de salud pública pequeños.
Contexto: plataforma "CitaSalud Arequipa" para reservar citas en centros de salud de la región.
Los pacientes buscan disponibilidad por especialidad y reservan/cancelan citas; el sistema envía
recordatorios por WhatsApp; el médico ve la lista de pacientes del día; el personal de admisión
administra cupos. ~5000 pacientes intentan reservar entre las 7:00 y las 7:15 a. m.
Restricciones: equipo de 3 developers que dominan Python/Django, PostgreSQL, MySQL, Node.js,
Angular, React, Java y C/C++; presupuesto de hosting bajo (un servidor VPS en la nube);
MVP en producción en 1 mes; ninguna cita puede asignarse dos veces; se manejan datos de salud
(Ley 29733 de protección de datos personales).
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas,
debilidades, riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

**Prompt 2 (entrada 2)**
```
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que recomendaste:
¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?,
¿qué costo oculto tiene? Enumera los 5 riesgos más graves y, para cada uno, una táctica
arquitectónica de mitigación.
```

**Mensajes enviados a Claude en las entradas 3 a 8 (citados de la conversación)**
- Entrada 3: "el caso elegido es el citaSaludArequipa"; "somos 3 personas, manejamos django, postgresql, mysql, angular, node.js, react, python, java, c++, c, vuejs"; "con respecto al cálculo de referencia, me dice verificar, ¿cómo hago eso? ¿debo crear la aplicación?"
- Entrada 4: "ahora pasamos al E2"
- Entrada 5: "ahora E3"; después se pegó la imagen obtenida en mermaid.live para comprobarla.
- Entrada 6: "ahora el e5"; después se pegó la imagen generada en plantuml.com para comprobarla.
- Entrada 7: "ahora dame el E6"; "pero no debería ser otro?"; "pero gunicorn, Redis, Prometheus y Grafana no hemos usado"
- Entrada 8: "antes del e7, falta armar el ADR de stack"
