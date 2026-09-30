# Drivers arquitectónicos — CitaSalud Arequipa

## 1. Requisitos funcionales clave
| ID    | Requisito                                                        | Actor              | Prioridad |
|-------|------------------------------------------------------------------|--------------------|-----------|
| RF-01 | Buscar disponibilidad de cupos por especialidad y centro de salud | Paciente           | Alta      |
| RF-02 | Reservar una cita en un cupo disponible                           | Paciente           | Alta      |
| RF-03 | Cancelar una cita y liberar el cupo                               | Paciente           | Alta      |
| RF-04 | Enviar recordatorio de la cita por WhatsApp                       | Sistema            | Media     |
| RF-05 | Ver la lista de pacientes citados del día                         | Médico             | Alta      |
| RF-06 | Administrar cupos/agenda y registrar citas en mostrador           | Personal de admisión | Alta    |
| RF-07 | Autenticar usuarios y restringir funciones según su rol           | Todos              | Alta      |

## 2. Atributos de calidad (ordenados por prioridad)
1. **Disponibilidad y rendimiento** — crítico: 5000 pacientes intentan reservar entre 7:00 y 7:15 a. m.; si el sistema cae o se demora, se pierde el acceso a la atención.
2. **Fiabilidad (integridad de datos)** — una cita asignada dos veces significa dos pacientes para un mismo cupo médico.
3. **Seguridad** — se manejan datos de salud, que son datos personales sensibles (Ley 29733).
4. **Modificabilidad** — se prevén nuevos canales de recordatorio (SMS, correo) y nuevas reglas por centro de salud.
5. **Capacidad de interacción** — pacientes con celulares y conectividad variables deben reservar en pocos pasos.

## 3. Restricciones
| ID   | Tipo        | Restricción                                                              |
|------|-------------|--------------------------------------------------------------------------|
| R-01 | Plazo       | MVP en producción en 1 mes                                               |
| R-02 | Equipo      | 3 developers; dominan Python/Django, PostgreSQL, MySQL, Node.js, React, Vue.js, Java y C/C++ |
| R-03 | Presupuesto | Bajo: un servidor (VPS) en la nube; cualquier servicio de pago se justifica |
| R-04 | Normativa   | Ley 29733 de protección de datos personales (datos de salud)             |
| R-05 | Tecnología  | Recordatorios obligatorios por WhatsApp (API externa, no controlada por el equipo) |

## 4. Escenarios de atributos de calidad
| ID    | Atributo          | Fuente                              | Estímulo                                   | Entorno                               | Artefacto                  | Respuesta                                                        | Medida                                   |
|-------|-------------------|-------------------------------------|--------------------------------------------|---------------------------------------|----------------------------|------------------------------------------------------------------|------------------------------------------|
| QA-01 | Rendimiento       | 5000 pacientes                      | Buscan y reservan una cita                 | Pico 7:00–7:15 a. m., operación normal | Módulos Disponibilidad y Reservas | Muestra cupos y confirma la reserva                       | p95 ≤ 3 s; disponibilidad ≥ 99 % en la ventana |
| QA-02 | Fiabilidad (integridad) | 2 o más pacientes a la vez    | Reservan el mismo cupo simultáneamente     | Pico de carga                          | Módulo Reservas + BD       | Confirma solo a uno; a los demás les informa que el cupo se ocupó | 0 cupos asignados dos veces en 10 000 intentos concurrentes de prueba |
| QA-03 | Seguridad         | Usuario autenticado con rol Paciente | Intenta ver la cita de otro paciente      | Operación normal                       | API de Reservas / Identidad | Deniega el acceso y registra el intento                         | 100 % de 50 intentos de prueba denegados (HTTP 403), 100 % registrados |

> Estimación de referencia: 5000 pacientes en 15 min (900 s) ≈ 5,6 reservas/s en promedio. Suponiendo ~8 peticiones por sesión (login, especialidad, cupos, filtro, confirmación, etc.), el pico es del orden de 40–50 peticiones/s. Es una estimación de diseño; se validaría con una prueba de carga sobre el prototipo..