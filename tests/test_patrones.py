from src.reservas.politicas import FabricaPoliticas, PoliticaAsignacionCupo

def test_open_closed_nueva_politica_sin_modificar_el_servicio():
    class PoliticaNueva(PoliticaAsignacionCupo):
        def buscar_cupo(self, especialidad, cupos_db):
            return True
            
    fabrica = FabricaPoliticas()
    fabrica._creadores["NUEVA"] = PoliticaNueva  # Registro dinámico
    
    politica = fabrica.crear("NUEVA")
    assert isinstance(politica, PoliticaNueva)