import pytest
from src.reservas.antes.servicio import ServicioReservasAntes, Cita

@pytest.fixture
def servicio():
    return ServicioReservasAntes()

def test_reserva_con_cupo_disponible_devuelve_cita_reservada(servicio):
    cita = Cita(1, "12345678", "999888777", "Medicina General")
    assert servicio.reservar_cita(cita) == "RESERVADA"
    assert cita.cupo_ocupado is True

def test_reserva_programa_recordatorio_por_whatsapp(servicio):
    cita = Cita(1, "12345678", "999888777", "Medicina General")
    servicio.reservar_cita(cita)
    assert "whatsapp: 999888777: Cita 1 reservada" in servicio.eventos

def test_cupo_ocupado_lanza_error_con_politica_estricta(servicio):
    cita = Cita(2, "12345678", "999888777", "Cardiologia")
    with pytest.raises(ValueError, match="No hay cupos alternativos"):
        servicio.reservar_cita(cita, politica_alternativos="MISMO_MEDICO")

def test_paciente_dni_invalido_lanza_error(servicio):
    cita = Cita(3, "123", "999888777", "Medicina General")
    with pytest.raises(ValueError, match="DNI inválido"):
        servicio.reservar_cita(cita)

def test_reserva_cita_ya_reservada_lanza_error(servicio):
    cita = Cita(4, "12345678", "999888777", "Medicina General", estado="RESERVADA")
    with pytest.raises(ValueError, match="La cita ya está reservada"):
        servicio.reservar_cita(cita)

def test_politica_no_soportada_lanza_error(servicio):
    cita = Cita(5, "12345678", "999888777", "Cardiologia")
    with pytest.raises(ValueError, match="Política no soportada"):
        servicio.reservar_cita(cita, politica_alternativos="INVENTADA")