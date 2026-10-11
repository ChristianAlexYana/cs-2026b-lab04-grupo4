# Auditoría de Consistencia (C1-C5)

| Regla | Hallazgo de la IA | Verificación del equipo | Decisión |
|---|---|---|---|
| C1 | `Cupo.ocupar()` no devuelve ningún valor, pero se asume que valida si se puede ocupar el cupo en el diagrama de secuencia. | **Falso positivo:** La IA interpretó mal el flujo. En el diagrama de secuencia se llama explícitamente a `estaDisponible()` antes para hacer la validación en el bloque `alt`, y `ocupar()` solo muta el estado. | Rechazado |
| C4 | El módulo "Notificaciones" depende de "Reservas", lo que podría considerarse un ciclo si "Reservas" usa "Notificaciones". | **Falso positivo:** La IA leyó la flecha `..>` de implementación de interfaz pero ignoró que el ADR-005 (Inversión de dependencias) precisamente movió el puerto a Reservas para que Reservas sea agnóstico de Notificaciones. No hay ciclo. | Rechazado |
| C5 | La operación `buscarAlternativos` en `ServicioDisponibilidad` está en camelCase, acorde a Java/TS, pero el equipo programará en Python (E6). | **Correcto:** La convención en Python es `snake_case` (`buscar_alternativos`). | Aceptado como advertencia; se manejará la conversión de nomenclatura en la implementación del código. |