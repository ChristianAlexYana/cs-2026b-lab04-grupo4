# ADR-009: Aislamiento multi-establecimiento con RLS
- **Estado:** Aceptado
- **Fecha:** 2026-10-31
- **Decisores:** Equipo 04 (Sergio, Christian, Renzo)

## Contexto
El escenario `QA-03` exige aislar la información clínica y de cupos de 40 establecimientos de salud distintos dentro de una misma infraestructura.

## Decisión
Implementar Row-Level Security (RLS) directamente en PostgreSQL, inyectando el ID del establecimiento desde la API mediante `SET LOCAL` en cada transacción.

## Consecuencias
(+) Garantiza 0 fugas de información entre centros incluso ante errores humanos en el ORM.
(-) Aumenta la complejidad del despliegue SQL y añade una leve latencia de 1-2 ms por petición.