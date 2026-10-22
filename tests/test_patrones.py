import pytest
from src.reservas.estados import CitaContexto
from src.reservas.politicas import FabricaPoliticas, PoliticaAsignacionCupo

def test_open_closed_nueva_politica_sin_modificar_el_servicio():
    class PoliticaNueva(PoliticaAsignacionCupo):
        def buscar_cupo(self, especialidad, cupos_db):
            return True
            
    fabrica = FabricaPoliticas()
    fabrica._creadores["NUEVA"] = PoliticaNueva  # Registro dinámico
    
    politica = fabrica.crear("NUEVA")
    assert isinstance(politica, PoliticaNueva)

def test_transicion_invalida_lanza_error_por_patron_state():
    cita = CitaContexto()
    cita.reservar() # Pasa a Reservada
    cita.cancelar() # Pasa a Cancelada
    
    with pytest.raises(ValueError, match="No se puede reservar una cita en estado CANCELADA"):
        cita.reservar() # Transición prohibida