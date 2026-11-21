# Issue 2: el DNI acepta letras y espacios

**Reportado por:** admisión (RF-02, Ley 29733).
**Observado:** un DNI como `ABCDEFGH` o `1234567A` pasa la validación porque solo se revisa que tenga 8 caracteres.
**Esperado:** un DNI válido tiene exactamente 8 dígitos numéricos; si no, "DNI inválido".
**Prueba que reproduce el error:** `tests/test_issue_02.py::test_issue_02_dni_de_ocho_caracteres_no_numericos_es_invalido`
**Pista de ubicación:** `src/reservas/externos.py` (simulación de RENIEC) o `src/reservas/adaptadores.py` (`DniAdapter`).
