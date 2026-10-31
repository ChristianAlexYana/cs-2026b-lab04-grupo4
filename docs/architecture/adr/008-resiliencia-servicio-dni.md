# ADR-008: Resiliencia ante caída del servicio de DNI
- **Estado:** Aceptado
- **Fecha:** 2026-10-31
- **Decisores:** Equipo 04 (Sergio, Christian, Renzo)

## Contexto
El escenario `QA-02` aborda la caída frecuente del servicio externo de validación de identidad, lo cual podría saturar los workers de CitaSalud (Riesgo R1).

## Decisión
Envolver el `DniAdapter` con los patrones Circuit Breaker y ConReintentos (timeout corto), permitiendo una reserva con estado "Pendiente de Validación" (degradación elegante).

## Consecuencias
(+) Se asegura que 0 operaciones de reserva se pierdan durante la interrupción del servicio externo.
(-) Añade complejidad en la gestión de estados pendientes.