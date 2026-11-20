"""Issue 2: el validador de DNI acepta cualquier texto de 8 caracteres."""
import pytest

from src.reservas.antes.servicio import Cita
from src.reservas.despues.servicio import ServicioReservasDespues


@pytest.mark.parametrize("dni", ["ABCDEFGH", "1234567A", "12 45678"])
def test_issue_02_dni_de_ocho_caracteres_no_numericos_es_invalido(dni):
    servicio = ServicioReservasDespues()
    with pytest.raises(ValueError, match="DNI inválido"):
        servicio.reservar_cita(Cita(1, dni, "999888777", "Medicina General"))
