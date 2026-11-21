"""Issue 1: la misma especialidad con un solo cupo se puede reservar dos veces."""
import pytest

from src.reservas.antes.servicio import Cita
from src.reservas.despues.servicio import ServicioReservasDespues


def test_issue_01_no_permite_dos_citas_en_el_mismo_cupo():
    servicio = ServicioReservasDespues()
    primera = Cita(1, "12345678", "999888777", "Medicina General")
    segunda = Cita(2, "87654321", "999111222", "Medicina General")
    assert servicio.reservar_cita(primera, politica_alternativos="MISMO_MEDICO") == "RESERVADA"
    with pytest.raises(ValueError, match="No hay cupos alternativos"):
        servicio.reservar_cita(segunda, politica_alternativos="MISMO_MEDICO")
