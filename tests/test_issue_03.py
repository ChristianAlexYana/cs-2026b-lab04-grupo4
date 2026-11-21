"""Issue 3: se programa el recordatorio de WhatsApp aunque la cita ya esté cancelada."""
from src.reservas.antes.servicio import Cita
from src.reservas.eventos import NotificadorWhatsApp
from src.reservas.puertos import Notificador


class NotificadorEspia(Notificador):
    def __init__(self):
        self.enviados = []

    def programar_recordatorio(self, cita) -> None:
        self.enviados.append(cita.id)


def test_issue_03_no_envia_recordatorio_a_cita_cancelada():
    espia = NotificadorEspia()
    suscriptor = NotificadorWhatsApp(espia)
    cancelada = Cita(7, "12345678", "999888777", "Medicina General", estado="CANCELADA")
    suscriptor.actualizar("CITA_RESERVADA", cancelada)
    assert espia.enviados == []
