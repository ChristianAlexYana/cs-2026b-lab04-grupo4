"""Pruebas unitarias del propio agente (Albada, 2025, cap. 9): contrato, política y sandbox."""
import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.politica import Politica
from agente.herramientas import Herramientas

H = {"leer_archivo", "editar_archivo", "ejecutar_comando"}

@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                      # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                   # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),    # ambas formas
    ("leer_archivo(a.py)", False),                                            # texto libre, no JSON
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado

def test_politica_bloquea_comandos_de_red_y_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}, 1).permitido

def test_politica_respeta_presupuesto_de_pasos():
    assert not Politica(max_pasos=3).evaluar("leer_archivo", {"ruta": "a"}, 4).permitido

def test_sandbox_impide_salir_del_directorio(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).leer_archivo("../../etc/passwd")



# --- E3: decisiones inválidas propias de CitaSalud (el contrato debe rechazarlas) ---
@pytest.mark.parametrize("d, motivo", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {}, "confianza": 0.9}, "campo de más"),
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": "issues/ISSUE-01.md"}, "args como texto"),
    ({"pensamiento": "leo", "accion": ""}, "acción vacía"),
    ({"pensamiento": "   ", "accion": "leer_archivo"}, "pensamiento en blanco"),
    ({"pensamiento": "listo", "final": 42}, "final que no es texto"),
    ('{“pensamiento”: “x”, “accion”: “leer_archivo”}', "comillas tipográficas: texto libre, no JSON"),
])
def test_contrato_rechaza_decisiones_invalidas_de_citasalud(d, motivo):
    ok, _ = validar_decision(d, H)
    assert ok is False, motivo