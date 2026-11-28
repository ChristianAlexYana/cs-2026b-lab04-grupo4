"""E7: pruebas de las dos reglas nuevas del auditor y de su resultado sobre los dos servidores."""
import asyncio, pathlib, sys
import pytest
from mcp.types import Tool, ToolAnnotations

MCP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MCP / "cliente"))
import auditar                                            # noqa: E402


def herramienta(anot=None, props=None, desc="Hace una consulta simple."):
    return Tool(name="t", description=desc, annotations=anot,
                input_schema={"type": "object", "properties": props or {}})


def motivos(tool):
    return [m for _, _, m in auditar.hallazgos_de(tool)]


# ---- Regla 1: escritura sin destructiveHint explícito
def test_regla1_marca_escritura_sin_destructive_hint():
    t = herramienta(ToolAnnotations(read_only_hint=False))
    assert any("destructiveHint" in m for m in motivos(t))


def test_regla1_marca_anotaciones_sin_read_only_hint_ni_destructive_hint():
    assert any("destructiveHint" in m for m in motivos(herramienta(ToolAnnotations(open_world_hint=False))))


def test_regla1_no_marca_escritura_que_declara_destructive_hint():
    t = herramienta(ToolAnnotations(read_only_hint=False, destructive_hint=False))
    assert not any("destructiveHint" in m for m in motivos(t))


def test_regla1_no_marca_herramientas_de_solo_lectura():
    assert not any("destructiveHint" in m for m in motivos(herramienta(ToolAnnotations(read_only_hint=True))))


# ---- Regla 2: texto libre sin límite en el esquema
def test_regla2_marca_texto_sin_limite():
    t = herramienta(ToolAnnotations(read_only_hint=True), {"nota": {"type": "string"}, "otra": {"type": "string"}})
    h = [m for m in motivos(t) if "texto libre" in m]
    assert h == ["texto libre sin límite en el esquema: nota, otra"]


@pytest.mark.parametrize("limite", [{"maxLength": 8}, {"enum": ["a", "b"]}, {"pattern": "^[0-9]{8}$"}])
def test_regla2_no_marca_texto_acotado(limite):
    t = herramienta(ToolAnnotations(read_only_hint=True), {"dni": {"type": "string", **limite}})
    assert not any("texto libre" in m for m in motivos(t))


def test_regla2_ignora_parametros_que_no_son_texto():
    t = herramienta(ToolAnnotations(read_only_hint=True), {"dias": {"type": "integer"}})
    assert not any("texto libre" in m for m in motivos(t))


# ---- Resultado sobre los servidores reales
def test_servidor_propio_no_tiene_hallazgos_altos_y_reporta_texto_libre(capsys):
    alto = asyncio.run(auditar.auditar(str(MCP / "servidor_mcp/citasalud_mcp.py")))
    salida = capsys.readouterr().out
    assert alto is False and "[ALTA ]" not in salida
    assert "texto libre sin límite en el esquema: celular, dni, especialidad" in salida


def test_servidor_de_terceros_tiene_hallazgos_altos(capsys):
    alto = asyncio.run(auditar.auditar(str(MCP / "terceros/clima_mcp.py")))
    salida = capsys.readouterr().out
    assert alto is True
    assert "instrucciones ocultas dirigidas al modelo" in salida and "pide secretos o credenciales" in salida
