# Bitácora de uso de IA — CitaSalud Arequipa

> **BORRADOR.** Por ahora solo las entradas 1 y 2 (E2); las demás se agregan en E7. Antes de entregar: complete las celdas **[COMPLETAR]** con lo que su grupo realmente verificó, y reemplace o agregue entradas según sus propias interacciones. No declare verificaciones que no hicieron.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 30/09 | Claude | Prompt 1 adaptado: 3 alternativas para CitaSalud (1 mes, 3 devs, 1 VPS, pico 5000 en 15 min) | Monolito en capas, monolito modular y microservicios; recomendó monolito modular | Se comprobó que microservicios excede R-01 y R-02. **[COMPLETAR: qué discutió el grupo]** | Aceptada |
| 2 | 30/09 | Claude | Prompt 2: crítica adversarial al monolito modular | Riesgos: erosión de límites entre módulos, punto único de falla, contención de bloqueos en el pico, dependencia de WhatsApp, datos de salud | **[COMPLETAR: cuáles riesgos aplican y qué tácticas se adoptaron]** | Aceptada / Corregida |

## Anexo: prompts

**Prompt 1 (entrada 1)**
```
Actúa como arquitecto de software senior con experiencia en sistemas de salud pública pequeños.
Contexto: plataforma "CitaSalud Arequipa" para reservar citas en centros de salud de la región.
Pacientes buscan disponibilidad por especialidad y reservan/cancelan; recordatorio por WhatsApp;
el médico ve la lista de pacientes del día; ~5000 pacientes intentan reservar entre 7:00 y 7:15 a. m.
Restricciones: 3 developers que dominan Python/Django, PostgreSQL, MySQL, Node.js, React, Vue.js, Java y C/C++, presupuesto de hosting bajo (un VPS),
MVP en 1 mes, ninguna cita puede asignarse dos veces, datos de salud (Ley 29733).
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas, debilidades,
riesgos y qué atributos de calidad favorece o penaliza.
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

