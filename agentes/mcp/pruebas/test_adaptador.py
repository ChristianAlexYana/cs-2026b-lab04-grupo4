"""El agente del Lab 10 ve al servidor MCP como herramientas locales; la escritura exige aprobacion."""
import pathlib, sys
from mcp import StdioServerParameters
RAIZ = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "agentes"))
from agente.herramientas_mcp import HerramientasMCP      # noqa: E402
from agente.politica import Politica                      # noqa: E402


def test_adaptador_descubre_y_ejecuta_y_la_politica_exige_aprobacion():
    h = HerramientasMCP(StdioServerParameters(command=sys.executable,
                                              args=[str(RAIZ / "agentes/mcp/servidor_mcp/citasalud_mcp.py")]))
    try:
        assert {"cupos_disponibles", "citas_del_dia", "leer_recurso"} <= set(h.catalogo())
        salida = h.cupos_disponibles(especialidad="Medicina General")
        assert not salida.startswith("ERROR")
        assert "Medicina General" in salida and "true" in salida.lower()
        assert h.citas_del_dia(fecha="23/11/2026").startswith("ERROR")
        assert h.herramientas_de_escritura() == {"reservar_cita_borrador"}
        p = Politica(herramientas_permitidas=set(h.catalogo()), requieren_aprobacion=h.herramientas_de_escritura())
        args = {"dni": "99900001", "especialidad": "Cardiologia", "celular": "999000001"}
        assert not p.evaluar("reservar_cita_borrador", args, 1).permitido           # sin aprobador
        p.aprobar = lambda accion, a: False
        assert not p.evaluar("reservar_cita_borrador", args, 1).permitido           # humano responde "n"
        p.aprobar = lambda accion, a: True
        assert p.evaluar("reservar_cita_borrador", args, 1).permitido
        assert p.evaluar("cupos_disponibles", {"especialidad": "Medicina General"}, 1).permitido
    finally:
        h.cerrar()