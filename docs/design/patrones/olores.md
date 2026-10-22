# Olores de código en el módulo Reservas

| Olor detectado | Patrón (confirmar con la IA) | Principio SOLID | Decisión del equipo |
|---|---|---|---|
| if/elif que elige la política de asignación de cupos alternativos | Strategy + Factory | Abierto/cerrado | **Aceptado**. Permite agregar nuevas políticas sin tocar `reservar_cita`. |
| El servicio conoce los detalles de cada SDK (WhatsApp, DNI) | Adapter | Inversión de dependencias | **Aceptado**. El servicio dependerá de puertos (interfaces) y no de SDKs de terceros. |
| Condicionales anidados sobre estado de la cita | State | Abierto/cerrado, Liskov | **Aceptado**. Implementará `estados-cita.mmd` del Lab 05. |
| El servicio arma a mano los recordatorios y avisos | Observer | Responsabilidad única | **Aceptado**. Extraeremos la notificación. |
| Bloque de reintentos duplicado | Decorator | Abierto/cerrado | **Aceptado**. Se envolverán las notificaciones con reintentos transparentes. |
| IA Propuso: Singleton para las fábricas | Singleton | Inversión de dependencias | **RECHAZADO**. Introduce estado global y dificulta la inyección de dependencias en las pruebas (testabilidad). |