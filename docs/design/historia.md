# Historia de usuario crítica — CitaSalud Arequipa

**Caso:** CitaSalud Arequipa (continuación del Laboratorio 04, ADR-001: monolito modular con puertos y adaptadores).
**Módulos involucrados:** Disponibilidad y cupos, Reservas, Agenda médica, Notificaciones, Identidad y acceso.
**Requisitos cubiertos:** RF-02 (reservar), RF-04 (recordatorio por WhatsApp). Atributos de calidad: QA-01 (p95 ≤ 3 s) y QA-02 (0 cupos asignados dos veces).

## HU-02

Como **paciente**, quiero **reservar una cita en un cupo disponible** de una especialidad y centro de salud,
para **atenderme sin hacer cola presencial a primera hora**.

## Criterios de aceptación

**CA-1: reserva exitosa**
- **Dado** un paciente autenticado y un cupo DISPONIBLE,
- **Cuando** reserva ese cupo,
- **Entonces** se crea la cita en estado RESERVADA, el cupo queda OCUPADO y se programa un recordatorio por WhatsApp.

**CA-2: cupo ocupado por otro paciente (no doble asignación)**
- **Dado** un cupo que otro paciente reservó antes (o al mismo tiempo),
- **Cuando** el paciente intenta reservarlo,
- **Entonces** el sistema responde "cupo ocupado", no crea ninguna cita y le ofrece cupos alternativos de la misma especialidad.

**CA-3: falla del recordatorio**
- **Dado** que la API de WhatsApp no responde,
- **Cuando** se reserva la cita,
- **Entonces** la cita igual queda RESERVADA y el envío se reintenta en segundo plano (ADR-003).

**CA-4: cancelación**
- **Dado** una cita RESERVADA o CONFIRMADA antes de su hora,
- **Cuando** el paciente la cancela,
- **Entonces** la cita queda CANCELADA y el cupo vuelve a estar DISPONIBLE.

## Supuestos (a validar con el equipo)
- Cada médico pertenece a un solo centro de salud en el MVP.
- El estado CONFIRMADA se alcanza cuando el paciente confirma su asistencia a partir del recordatorio.
- Solo se guarda el celular del paciente (para WhatsApp); no se guardan DNI ni datos clínicos en este módulo (Ley 29733, R-04).