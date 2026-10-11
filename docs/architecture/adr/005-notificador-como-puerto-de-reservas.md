# ADR-005: Definir el puerto Notificador en el módulo Reservas

- Estado: Aceptado
- Fecha: 2026-10-10
- Decisores: Yana Huanca Christian Alexander, Estrada Arce Sergio Emilio y Mamani Quispe Renzo Geomar

## Contexto
Al dibujar `paquetes.puml` (E5, Lab 05) y verificar la regla C4 se detectó un ciclo de dependencias entre módulos. En `clases.puml` el puerto `Notificador` estaba en *Notificaciones*, pero su operación `programarRecordatorio(cita: Cita)` recibe una `Cita`, que pertenece a *Reservas*; a la vez, `ServicioReservas` (en *Reservas*) usa `Notificador`. Resultado: *Reservas* → *Notificaciones* y *Notificaciones* → *Reservas*. Esto contradice el ADR-001 (módulos que se comunican solo por interfaces públicas, integraciones externas como adaptadores) y el ADR-003 (la reserva no debe depender de WhatsApp).

## Alternativas consideradas
1. **Puerto `Notificador` en *Reservas*; en *Notificaciones* solo el adaptador `WhatsAppAdapter`.** El módulo que consume el puerto lo define (inversión de dependencias).
2. **Un DTO de recordatorio en un paquete `compartido`.** Elimina el ciclo, pero agrega un módulo que no está en el ADR-001 y un objeto extra para el MVP.
3. **Dejarlo como estaba.** Mantiene el ciclo; incumple C4.

## Decisión
Usaremos la alternativa 1: el puerto `Notificador` se define en el módulo *Reservas*. *Notificaciones* contiene `WhatsAppAdapter`, que realiza ese puerto y depende de *Reservas* (por `Cita`). *Reservas* ya no depende de *Notificaciones*.

## Consecuencias
Positivas: sin ciclos entre módulos (C4); el núcleo no depende del adaptador y se pueden agregar otros canales (SMS, correo) sin tocar *Reservas*; el mensaje asíncrono `programarRecordatorio(cita)` del diagrama de secuencia no cambia.
Negativas / riesgos: *Notificaciones* queda acoplado a *Reservas*; un recordatorio de otro tipo (no ligado a una cita) tendría que usar otro puerto. Se actualizaron `clases.puml` y su imagen para mantener la consistencia.
