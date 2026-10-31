# ADR-007: Caché de disponibilidad y control de concurrencia
- **Estado:** Aceptado
- **Fecha:** 2026-10-31
- **Decisores:** Equipo 04 (Sergio, Christian, Renzo)

## Contexto
El escenario `QA-01` requiere soportar un pico de 320–400 peticiones por segundo a las 7:00 a.m. sin que el p95 supere el umbral establecido.

## Decisión
Se decide implementar una caché de lectura de disponibilidad en Redis con un TTL corto y limitar el tamaño del pool de conexiones hacia PostgreSQL.

## Consecuencias
(+) Se mitiga el Riesgo R2, reduciendo drásticamente la latencia y la contención en base de datos.
(-) Introduce consistencia eventual en la vista de horarios (trade-off aceptado, la integridad se verifica al insertar).