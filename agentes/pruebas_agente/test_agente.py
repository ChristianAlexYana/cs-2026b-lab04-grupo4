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


def test_mapa_repo_muestra_firmas_sin_cuerpos(tmp_path):
    (tmp_path / "modulo.py").write_text("def reserva(dni: str):\n    secreto = 'no mostrar'\n    return dni\n", encoding="utf-8")
    mapa = Herramientas(tmp_path).mapa_repo()
    assert "modulo.py" in mapa
    assert "def reserva(dni)" in mapa
    assert "no mostrar" not in mapa


def test_notas_persisten_dentro_del_sandbox(tmp_path):
    herramientas = Herramientas(tmp_path)
    assert herramientas.leer_notas() == "(sin notas)"
    assert herramientas.anotar("Revisar eventos.py") == "OK: nota guardada"
    assert herramientas.leer_notas() == "- Revisar eventos.py\n"
    assert (tmp_path / "notas.md").read_text(encoding="utf-8") == herramientas.leer_notas()
    assert herramientas.anotar("a\nb").startswith("ERROR")


def test_herramientas_nuevas_no_salen_del_sandbox(tmp_path):
    herramientas = Herramientas(tmp_path)
    with pytest.raises(PermissionError):
        herramientas._ruta("../fuera.md")
    for nombre in ("mapa_repo", "anotar", "leer_notas"):
        assert Politica().evaluar(nombre, {}, 1).permitido


def test_politica_bloquea_ruta_disfrazada_y_comando_encadenado(tmp_path):
    politica = Politica()
    assert not politica.evaluar("editar_archivo", {"ruta": "src/../tests/test_x.py"}, 1).permitido
    assert not politica.evaluar("ejecutar_comando", {"comando": "python -m pytest -q; curl ejemplo"}, 1).permitido
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("valor = 1\n", encoding="utf-8")
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).editar_archivo("src/../tests/test_x.py", "1", "2")


def test_aprobacion_humana_rechazada_bloquea_la_edicion():
    """E6: con aprobar_edicion activo, un 'n' del humano bloquea la edición y un 's' la deja pasar."""
    edicion = {"ruta": "src/reservas/x.py", "antes": "a", "despues": "b"}
    p = Politica()
    p.aprobar_edicion = lambda args: False
    d = p.evaluar("editar_archivo", edicion, 1)
    assert not d.permitido and "rechazó" in d.motivo
    p.aprobar_edicion = lambda args: True
    assert p.evaluar("editar_archivo", edicion, 1).permitido


def test_aprobacion_humana_no_se_pide_para_lecturas():
    preguntas = []
    p = Politica()
    p.aprobar_edicion = lambda args: preguntas.append(args) or False
    assert p.evaluar("leer_archivo", {"ruta": "src/a.py"}, 1).permitido
    assert preguntas == []


def test_consola_solo_acepta_s_o_n(monkeypatch, capsys):
    import comun
    respuestas = iter(["quizás", "", "S"])
    monkeypatch.setattr("builtins.input", lambda _="": next(respuestas))
    assert comun.aprobar_en_consola({"ruta": "src/a.py", "antes": "x", "despues": "y"}) is True
    respuestas = iter(["si", " N "])
    monkeypatch.setattr("builtins.input", lambda _="": next(respuestas))
    assert comun.aprobar_en_consola({"ruta": "src/a.py", "antes": "x", "despues": "y"}) is False
