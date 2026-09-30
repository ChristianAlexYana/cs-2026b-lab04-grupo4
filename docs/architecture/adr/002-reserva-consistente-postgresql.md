# ADR-002: Garantizar cupos únicos con PostgreSQL (índice único parcial y transacción)

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: Yana Huanca Christian Alexander, Estrada Arce Sergio Emilio y Mamani Quispe Renzo Geomar

## Contexto
Ninguna cita puede asignarse dos veces (QA-02) y hasta 5000 pacientes compiten por cupos entre las 7:00 y las 7:15 a. m. (QA-01). Se manejan datos de salud sujetos a la Ley 29733 (R-04) y el presupuesto permite un solo servidor (R-03). El equipo domina PostgreSQL y MySQL (R-02). Requisitos: RF-02, RF-03, RF-06.

## Alternativas consideradas
1. **PostgreSQL** con un índice único parcial sobre el cupo (solo para citas confirmadas) y una transacción por reserva.
2. **MySQL (InnoDB)** con restricción única; no tiene índices parciales nativos, así que liberar un cupo al cancelar requeriría una solución alternativa (p. ej., una columna generada). [Verificar en la documentación oficial de MySQL.]
3. **Bloqueo distribuido en Redis** antes de escribir en la BD: agrega una pieza más y un punto de falla, y la garantía final seguiría dependiendo de la BD.

## Decisión
Usaremos PostgreSQL. Cada cupo será una fila y la reserva se protegerá con un índice único parcial (un solo registro con estado "confirmada" por cupo), dentro de una transacción. Si dos pacientes compiten, el segundo recibe un error controlado ("cupo ocupado") y se le ofrecen cupos alternativos. Al cancelar, el cupo queda libre para otra reserva.

## Consecuencias
- Positivas: la garantía de no duplicidad la da la base de datos y no el código de la aplicación; se prueba fácilmente con intentos concurrentes (QA-02); no agrega servicios al servidor; el equipo ya domina PostgreSQL.
- Negativas / riesgos: la contención en cupos muy solicitados genera conflictos que la interfaz debe manejar con claridad; el pico concentra la carga en una sola BD (se mitiga con índices, pool de conexiones y pruebas de carga).
