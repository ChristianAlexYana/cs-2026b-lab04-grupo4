# ADR-003: Enviar recordatorios de WhatsApp mediante una cola de tareas asíncrona

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: Yana Huanca Christian Alexander, Estrada Arce Sergio Emilio y Mamani Quispe Renzo Geomar

## Contexto
Los recordatorios por WhatsApp son obligatorios (R-05, RF-04), pero la API externa puede responder lento o fallar, y eso no debe demorar ni impedir la reserva (QA-01). El módulo Notificaciones debe permitir agregar otros canales con poco esfuerzo (modificabilidad).

## Alternativas consideradas
1. Enviar el mensaje de forma síncrona dentro de la petición de reserva.
2. Publicar una tarea en una cola (Celery + Redis) que un worker procesa con reintentos.
3. Un cron que recorra las citas del día siguiente y envíe los mensajes en lote.

## Decisión
Usaremos Celery con Redis (el equipo domina Python/Django, R-02) como cola de tareas: al confirmar la cita se encola el recordatorio y un worker lo envía con reintentos y espera creciente. La reserva nunca depende de la respuesta de WhatsApp.

## Consecuencias
- Positivas: una caída de WhatsApp no afecta las reservas; los reintentos son configurables; un nuevo canal se agrega como otro adaptador del módulo Notificaciones.
- Negativas / riesgos: se suman Redis y un worker al VPS (más operación para 3 developers); hay que monitorear la cola y validar las condiciones de envío de WhatsApp Business (plantillas, límites) en su documentación oficial.
