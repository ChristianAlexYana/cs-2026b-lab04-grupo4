# ADR-010: Sistema agéntico para corregir issues de CitaSalud
- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Decisores:** Equipo 04 (Sergio, Christian, Renzo)

## Contexto
Queremos que un modelo ayude a resolver errores del código de reservas (cupo duplicado, DNI con letras, recordatorio a citas canceladas) sin poner en riesgo el repositorio ni los datos de pacientes. El caso toca validación de datos personales (RF-02, Ley 29733) y concurrencia de cupos (QA-02). El equipo es de tres personas y el plazo es de un laboratorio, así que el sistema debe ser simple de auditar y de repetir.

## Decisión
- **Arquetipo:** ReAct, un bucle de pensamiento, acción y observación modelado como máquina de estados (`agentes/diseno/estados.puml`, implementada en `agentes/agente/nucleo.py`).
- **Coordinación:** agente único para los issues 1 y 3. Para el issue 2, un actor-crítico (planificador, ejecutor y revisor de solo lectura, máximo 2 rondas). En la comparación de E5 el actor-crítico costó una acción y 3 232 caracteres más que el agente único y su revisor no encontró defectos; solo el planificador señaló los dígitos Unicode. Se conserva como opción para cambios de riesgo, no como valor por defecto (parsimonia).
- **Herramientas:** mínimas y por rol: `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`, `ejecutar_pruebas`, `editar_archivo`, `anotar`, `leer_notas` y `ejecutar_comando` limitado a pytest, radon cc, lint-imports y `git status`/`git diff`. El revisor no puede editar.
- **Memoria:** historial de la corrida (corto plazo) y notas en `notas.md` dentro del sandbox. Cada corrida parte de una copia limpia del repositorio.
- **Límites:** contrato JSON validado antes de actuar, política de herramientas, comandos y rutas, `tests/` protegida, máximo de 15 pasos (12 en el orquestador) y 2 rondas, sandbox en `agentes/trabajo/` y traza JSONL de cada corrida.
- **Rol humano:** revisor. Con `--aprobar`, cada edición espera «s» o «n»; una persona revisa el diff, aplica el cambio, corre pytest y hace el commit. Ningún agente fusiona su propio cambio. La ruta hacia más autonomía está en `agentes/delegacion.md`.

## Alternativas descartadas
- **Flujo de trabajo fijo para los tres issues:** no se conoce de antemano qué archivos hay que leer ni cuántas veces correr pruebas. Sí se mantiene un flujo fijo para el envío del recordatorio de WhatsApp.
- **Planificador-ejecutor y reflexivo como arquetipo base:** los issues tocan uno o dos archivos y el plan completo no se conoce hasta leer el código.
- **Actor-crítico para todos los issues:** más contexto y más pasos sin beneficio medido en el issue 2.
- **Edición directa sobre el repositorio y permisos amplios (shell libre, red):** exceso de agencia (OWASP LLM06) e inyección indirecta (Greshake et al., 2023); un archivo o issue podría contener instrucciones.
- **Agente autónomo con auto-merge:** sin evidencia suficiente para el rol de colaborador o gobernador (cuatro corridas).

## Consecuencias
(+) Cada decisión queda en una traza auditable; las pruebas del propio agente cubren contrato, política, sandbox y aprobación (`agentes/pruebas_agente/`).
(+) El bloqueo funciona: la política denegó `ver_cambios` al ejecutor y rechazó la edición cuando el humano respondió «n».
(-) Mucho trabajo manual: una persona pega cada decisión del asistente (`ModeloInteractivo`) y aplica el cambio; no se probó un asistente conectado por API.
(-) Muestra pequeña: cuatro corridas y tres issues, con un solo asistente; los números de pasos y contexto no son generalizables.
(-) No se evaluó inyección indirecta ni red teaming del agente (Laboratorio 13).
