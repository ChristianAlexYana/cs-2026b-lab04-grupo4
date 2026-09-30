# ADR-001: Adoptar un monolito modular para el MVP de CitaSalud Arequipa

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: [AJUSTAR: nombres de los 3 integrantes]

## Contexto
El MVP debe salir en 1 mes (R-01) con 3 developers (R-02) y un único VPS (R-03). El atributo crítico es la disponibilidad y el rendimiento en el pico de 5000 pacientes entre 7:00 y 7:15 a. m. (QA-01), sin asignar nunca una cita dos veces (QA-02). Se prevén nuevos canales de recordatorio y reglas por centro de salud (modificabilidad). Requisitos cubiertos: RF-01 a RF-07.

## Alternativas consideradas
1. Monolito en capas (4,10): simple y barato, pero sin límites por dominio; la modificabilidad es baja.
2. Microservicios (2,75): más escalables, pero 5 despliegues, varias BD y un broker exceden al equipo (R-01, R-02) y complican la consistencia de las reservas (QA-02).
3. Monolito modular (4,20): elegido. Puntajes en `matriz-decision.md`.

## Decisión
Usaremos un monolito modular con 5 módulos (Disponibilidad y cupos, Reservas, Agenda médica, Notificaciones, Identidad y acceso). Los módulos se comunican solo mediante interfaces públicas (servicios de aplicación) y cada uno tiene su propio esquema en PostgreSQL. Las integraciones externas (WhatsApp) se implementan como adaptadores.

## Consecuencias
- Positivas: un solo despliegue, bajo costo, entrega en 1 mes; la reserva se resuelve en una transacción local (QA-02); los módulos pueden extraerse como servicios si la carga lo exige.
- Negativas / riesgos: el equipo debe respetar los límites entre módulos (linter de imports en la CI); una falla grave afecta a todo el sistema; el pico de 7:00 exige pruebas de carga previas.
