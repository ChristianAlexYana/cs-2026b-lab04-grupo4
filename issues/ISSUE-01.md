# Issue 1: se puede reservar dos veces el único cupo de una especialidad

**Reportado por:** personal de admisión del centro de salud.
**Observado:** dos pacientes reservan "Medicina General" y los dos reciben la cita RESERVADA, aunque había un solo cupo.
**Esperado:** la segunda reserva debe fallar con "No hay cupos alternativos" cuando se usa la política MISMO_MEDICO.
**Prueba que reproduce el error:** `tests/test_issue_01.py::test_issue_01_no_permite_dos_citas_en_el_mismo_cupo`
**Pista de ubicación:** `src/reservas/despues/servicio.py` (`reservar_cita` y `_asegurar_cupo`).
