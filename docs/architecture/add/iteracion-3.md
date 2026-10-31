# Iteración 3 de ADD: Aislamiento Multi-Establecimiento

## Paso 1: Revisar entradas
- **Objetivo:** Atender el escenario de seguridad `QA-03` (Confidencialidad).
- **Escenario:** Al escalar a 40 establecimientos de salud, un usuario (personal de admisión o médico) intenta acceder a las citas o cupos de un establecimiento distinto al suyo. El sistema deniega el acceso al 100% de los intentos no autorizados, asegurando 0 fugas de datos y sumando $\le 5\text{ ms}$ de sobrecarga.

## Pasos 2 y 3: Identificar tácticas candidatas y seleccionar
Dado el estilo arquitectónico de monolito modular (`ADR-001`) y el presupuesto de un solo servidor VPS, evaluamos tres tácticas para aislar los datos:

| Táctica | Beneficios | Costos / Riesgos | Decisión |
|---|---|---|---|
| **A. Bases de datos separadas (1 por centro)** | Aislamiento físico 100% seguro. Imposible cruzar datos. | Excede el presupuesto de RAM/CPU de un VPS. Migraciones inviables para 3 developers en 1 mes. | **Rechazada.** Rompe la restricción de infraestructura y plazo. |
| **B. Filtrado manual en el ORM (Django)** | Cero impacto en infraestructura. Muy rápido de programar inicialmente. | Alta probabilidad de error humano (olvidar un `.filter(establecimiento=...)` expone los datos). | **Rechazada.** No garantiza el 100% de aislamiento a largo plazo. |
| **C. Row-Level Security (RLS) en PostgreSQL + Autorización en API** | Aislamiento garantizado por el motor de base de datos independientemente del código backend. | Añade ~1-2 ms de sobrecarga al inyectar el contexto de sesión (`SET LOCAL`) por petición. | **Elegida.** Equilibra alta seguridad con bajo impacto en infraestructura. |

## Pasos 4 a 7: Análisis y responsabilidades
- **Elementos afectados:** Base de datos PostgreSQL (esquemas y políticas RLS), Módulo `Identidad y acceso` (manejo de tokens y establecimiento asignado).
- **Trade-off aceptado:** Se asume un leve incremento en el tiempo de conexión a la BD (~1-2 ms por petición) a cambio de blindar el acceso a nivel de motor SQL, previniendo errores a nivel de aplicación (ORM).