# Issue 3: el recordatorio de WhatsApp se envía a citas canceladas

**Reportado por:** pacientes (RF-04).
**Observado:** si una cita ya figura como CANCELADA, el suscriptor de WhatsApp igual programa el recordatorio.
**Esperado:** solo las citas activas (no canceladas) reciben recordatorio.
**Prueba que reproduce el error:** `tests/test_issue_03.py::test_issue_03_no_envia_recordatorio_a_cita_cancelada`
**Pista de ubicación:** `src/reservas/eventos.py` (`NotificadorWhatsApp.actualizar`).
