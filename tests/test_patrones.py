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
# ---------- E4: Observer ----------
from types import SimpleNamespace

from src.reservas.adaptadores import WhatsAppAdapter
from src.reservas.eventos import (
    NotificadorWhatsApp,
    PublicadorEventos,
    Suscriptor,
    SuscriptorAuditoria,
)
from src.reservas.externos import WhatsAppSDK


class WhatsAppSDKEspia(WhatsAppSDK):
    def __init__(self):
        self.enviados = []

    def enviar_mensaje(self, telefono, texto):
        self.enviados.append((telefono, texto))
        return {"ok": True, "id": "msg_test"}


def test_observer_notifica_a_todos_los_suscriptores():
    sdk = WhatsAppSDKEspia()
    auditoria = SuscriptorAuditoria()
    publicador = PublicadorEventos()
    publicador.suscribir(NotificadorWhatsApp(WhatsAppAdapter(sdk)))
    publicador.suscribir(auditoria)

    publicador.publicar("CITA_RESERVADA", SimpleNamespace(id=1, celular="999888777"))

    assert sdk.enviados == [("999888777", "Cita 1 reservada")]
    assert auditoria.registro == ["CITA_RESERVADA: cita 1"]


def test_observer_nuevo_suscriptor_sin_tocar_el_publicador():
    class SuscriptorContador(Suscriptor):
        def __init__(self):
            self.total = 0

        def actualizar(self, evento, cita):
            self.total += 1

    contador = SuscriptorContador()
    publicador = PublicadorEventos()
    publicador.suscribir(contador)

    publicador.publicar("CITA_RESERVADA", SimpleNamespace(id=2, celular="111"))

    assert contador.total == 1
# ---------- E4: Decorator ----------
from src.reservas.eventos import ConReintentos
from src.reservas.puertos import Notificador


class NotificadorFalso(Notificador):
    def __init__(self, errores):
        self.errores = list(errores)
        self.llamadas = 0

    def programar_recordatorio(self, cita):
        self.llamadas += 1
        if self.errores:
            raise self.errores.pop(0)


def test_decorator_reintenta_solo_ante_timeout():
    falso = NotificadorFalso([TimeoutError(), TimeoutError()])
    ConReintentos(falso).programar_recordatorio(SimpleNamespace(id=1, celular="111"))
    assert falso.llamadas == 3


def test_decorator_no_reintenta_si_el_resultado_es_rechazado():
    falso = NotificadorFalso([ValueError("rechazado")])
    with pytest.raises(ValueError):
        ConReintentos(falso).programar_recordatorio(SimpleNamespace(id=1, celular="111"))
    assert falso.llamadas == 1


def test_decorator_propaga_timeout_al_agotar_intentos():
    falso = NotificadorFalso([TimeoutError()] * 3)
    with pytest.raises(TimeoutError):
        ConReintentos(falso).programar_recordatorio(SimpleNamespace(id=1, celular="111"))
    assert falso.llamadas == 3

# ---------- E5: IA aislada ----------
from src.reservas.ia import (
    ClasificadorMotivo,
    LLMSimuladoAdapter,
    LLMSimuladoSDK,
    ProveedorLLM,
)


def test_ia_clasifica_motivo_con_llm_simulado():
    sdk = LLMSimuladoSDK("Cardiologia")
    clasificador = ClasificadorMotivo(LLMSimuladoAdapter(sdk))

    assert clasificador.sugerir_especialidad("dolor en el pecho") == "Cardiologia"
    assert sdk.llamadas == 1


def test_ia_proveedor_intercambiable_sin_tocar_el_clasificador():
    class ProveedorFijo(ProveedorLLM):
        def completar(self, prompt):
            return "Pediatria"

    clasificador = ClasificadorMotivo(ProveedorFijo())

    assert clasificador.sugerir_especialidad("fiebre en un niño") == "Pediatria"
# ---------- E5: Decorator de caché ----------
from src.reservas.ia import ConCache


def test_ia_cache_evita_llamadas_repetidas():
    sdk = LLMSimuladoSDK("Cardiologia")
    proveedor = ConCache(LLMSimuladoAdapter(sdk))

    assert proveedor.completar("dolor en el pecho") == "Cardiologia"
    assert proveedor.completar("dolor en el pecho") == "Cardiologia"
    assert sdk.llamadas == 1

    proveedor.completar("tos persistente")
    assert sdk.llamadas == 2


def test_ia_cache_no_guarda_las_respuestas_fallidas():
    class ProveedorQueFallaUnaVez(ProveedorLLM):
        def __init__(self):
            self.llamadas = 0

        def completar(self, prompt):
            self.llamadas += 1
            if self.llamadas == 1:
                raise TimeoutError()
            return "Pediatria"

    interno = ProveedorQueFallaUnaVez()
    proveedor = ConCache(interno)

    with pytest.raises(TimeoutError):
        proveedor.completar("fiebre")
    assert proveedor.completar("fiebre") == "Pediatria"
    assert interno.llamadas == 2
# ---------- E5: Guardrails (Chain of Responsibility) ----------
from src.reservas.ia import ConGuardrails, crear_cadena_guardrails


def test_guardrails_dejan_pasar_una_respuesta_valida():
    proveedor = ConGuardrails(
        LLMSimuladoAdapter(LLMSimuladoSDK("Cardiologia")), crear_cadena_guardrails()
    )

    assert proveedor.completar("dolor en el pecho") == "Cardiologia"


@pytest.mark.parametrize(
    "respuesta_invalida, mensaje",
    [
        ("Usted tiene gripe", "diagnóstico"),
        ("Astrologia", "catálogo"),
        ("Medicina General" * 5, "demasiado larga"),
    ],
)
def test_guardrails_bloquean_respuestas_invalidas(respuesta_invalida, mensaje):
    proveedor = ConGuardrails(
        LLMSimuladoAdapter(LLMSimuladoSDK(respuesta_invalida)), crear_cadena_guardrails()
    )

    with pytest.raises(ValueError, match=mensaje):
        proveedor.completar("cualquier motivo")


def test_respuesta_bloqueada_no_se_guarda_en_la_cache():
    sdk = LLMSimuladoSDK("Usted tiene gripe")
    proveedor = ConCache(ConGuardrails(LLMSimuladoAdapter(sdk), crear_cadena_guardrails()))

    for _ in range(2):
        with pytest.raises(ValueError):
            proveedor.completar("tos")

    assert sdk.llamadas == 2