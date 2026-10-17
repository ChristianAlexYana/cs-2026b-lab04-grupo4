# Inventario de Elementos del Modelo C4 — CitaSalud Arequipa

| Elemento | Tipo C4 | Origen |
|---|---|---|
| Paciente, Personal de admisión, Médico | Persona | `docs/architecture/drivers.md` (Lab 04) |
| CitaSalud Arequipa | Sistema de software | Caso de estudio (`drivers.md`, Lab 04) |
| WhatsApp Business API, Servicio de consulta de DNI (RENIEC) | Sistema externo | `docs/architecture/drivers.md` y `ADR-001` / `ADR-003` (Lab 04) |
| Aplicación web progresiva (PWA), API CitaSalud, Worker de recordatorios, Base de datos (PostgreSQL), Cola de tareas (Redis) | Contenedor | `ADR-001`, `ADR-002`, `ADR-003`, `ADR-004` y `despliegue.py` (Lab 04) |
| Módulo Disponibilidad y cupos, Módulo Reservas, Módulo Agenda médica, Módulo Notificaciones, Módulo Identidad y acceso | Componente (de la API) | `docs/design/paquetes.puml` y `clases.puml` (Lab 05) |
| Flujo "Reservar una cita verificando cupo y evitando doble asignación" | Vista dinámica | `docs/design/secuencia-reservar-cita.puml` (Lab 05) |