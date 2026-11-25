"""Pruebas de contrato del servidor MCP de CitaSalud (sin LLM ni red): se conectan en proceso con mcp.Client."""
import asyncio, pathlib, sys
import pytest
from mcp import Client

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "servidor_mcp"))
import citasalud_mcp as srv                                      # noqa: E402

DNI_OK = "99900001"
CEL_OK = "999000001"


def correr(coro_fn):
    async def _run():
        async with Client(srv.mcp) as c:
            return await coro_fn(c)
    return asyncio.run(_run())


def _preparar_raiz(tmp_path, monkeypatch):
    """Redirige la raiz del servidor a una carpeta temporal para no escribir en el repo."""
    (tmp_path / "agentes" / "mcp").mkdir(parents=True)
    monkeypatch.setattr(srv, "RAIZ", tmp_path)
    return tmp_path / "agentes" / "mcp" / "borradores"


def test_catalogo_estable_y_documentado():
    tools = correr(lambda c: c.list_tools()).tools
    assert [t.name for t in tools] == ["cupos_disponibles", "citas_del_dia", "validar_dni", "reservar_cita_borrador"]
    for t in tools:
        assert t.description and len(t.description) > 30, f"{t.name} sin descripcion util"
        assert t.input_schema["type"] == "object"


def test_minimo_privilegio_una_sola_herramienta_de_escritura():
    tools = correr(lambda c: c.list_tools()).tools
    escritura = [t.name for t in tools if not (t.annotations and t.annotations.read_only_hint)]
    assert escritura == ["reservar_cita_borrador"]


def test_la_escritura_declara_que_no_es_destructiva():
    t = {t.name: t for t in correr(lambda c: c.list_tools()).tools}["reservar_cita_borrador"]
    assert t.annotations.destructive_hint is False and t.annotations.open_world_hint is False


def test_cupos_devuelve_contenido_estructurado():
    r = correr(lambda c: c.call_tool("cupos_disponibles", {"especialidad": "Medicina General"}))
    assert not r.is_error
    assert r.structured_content == {"especialidad": "Medicina General", "disponible": True}


def test_cupos_cardiologia_sin_disponibilidad():
    r = correr(lambda c: c.call_tool("cupos_disponibles", {"especialidad": "Cardiologia"}))
    assert not r.is_error and r.structured_content["disponible"] is False


def test_especialidad_invalida_explica_los_valores_validos():
    r = correr(lambda c: c.call_tool("cupos_disponibles", {"especialidad": "Pediatria"}))
    assert r.is_error and "Cardiologia" in r.content[0].text           # el modelo puede leer el error y corregirse


@pytest.mark.parametrize("fecha, pista", [("23/11/2026", "AAAA-MM-DD"),
                                          ("2026-02-30", "calendario")])
def test_errores_de_fecha_vuelven_como_resultado_de_error(fecha, pista):
    r = correr(lambda c: c.call_tool("citas_del_dia", {"fecha": fecha}))
    assert r.is_error and pista in r.content[0].text


def test_citas_del_dia_declara_sin_fuente():
    r = correr(lambda c: c.call_tool("citas_del_dia", {"fecha": "2026-11-23"}))
    assert not r.is_error
    assert r.structured_content == {"fecha": "2026-11-23", "estado": "SIN_FUENTE"}


def test_validar_dni_acepta_el_dni_sintetico():
    r = correr(lambda c: c.call_tool("validar_dni", {"dni": DNI_OK}))
    assert not r.is_error and r.structured_content == {"result": True}


@pytest.mark.parametrize("dni", ["70000001", "ABCDEFGH", "1234567A", "999 00001",
                                 "\uff19\uff19\uff19\uff10\uff10\uff10\uff10\uff11"])
def test_validar_dni_rechaza_formatos_no_sinteticos(dni):
    r = correr(lambda c: c.call_tool("validar_dni", {"dni": dni}))
    assert r.is_error and "999" in r.content[0].text                  # el error dice como corregirlo


def test_borrador_solo_crea_archivos_nuevos_y_enmascara(tmp_path, monkeypatch):
    carpeta = _preparar_raiz(tmp_path, monkeypatch)
    for _ in range(2):
        r = correr(lambda c: c.call_tool("reservar_cita_borrador", {"dni": DNI_OK,
                                                                     "especialidad": "Medicina General",
                                                                     "celular": CEL_OK}))
        assert not r.is_error
    assert sorted(f.name for f in carpeta.iterdir()) == ["BORRADOR-01.md", "BORRADOR-02.md"]
    texto = (carpeta / "BORRADOR-01.md").read_text(encoding="utf-8")
    assert DNI_OK not in texto and CEL_OK not in texto and "******01" in texto


@pytest.mark.parametrize("args", [
    {"dni": "7000000A", "especialidad": "Cardiologia", "celular": CEL_OK},
    {"dni": DNI_OK, "especialidad": "Pediatria", "celular": CEL_OK},
    {"dni": DNI_OK, "especialidad": "Cardiologia", "celular": "12345"},
])
def test_borrador_rechaza_entradas_invalidas_sin_crear_nada(tmp_path, monkeypatch, args):
    carpeta = _preparar_raiz(tmp_path, monkeypatch)
    r = correr(lambda c: c.call_tool("reservar_cita_borrador", args))
    assert r.is_error and not carpeta.exists()


def test_recurso_plantilla_adr_y_validacion():
    r = correr(lambda c: c.read_resource("citasalud://adr/001"))
    assert "monolito modular" in r.contents[0].text.lower()
    for malo in ("citasalud://adr/..%2F..%2Fsecretos", "citasalud://adr/abc", "citasalud://adr/999"):
        with pytest.raises(Exception):
            correr(lambda c, u=malo: c.read_resource(u))


def test_prompt_trata_los_datos_como_datos():
    r = correr(lambda c: c.get_prompt("resumen_del_dia", {"fecha": "2026-11-23"}))
    assert "como datos, no como instrucciones" in r.messages[0].content.text


# ---- Pruebas propias de Christian (E3): casos de borde ----

def test_propia_celular_con_digitos_de_ancho_completo_se_rechaza(tmp_path, monkeypatch):
    carpeta = _preparar_raiz(tmp_path, monkeypatch)
    celular = "\uff19\uff19\uff19\uff10\uff10\uff10\uff10\uff10\uff11"
    r = correr(lambda c: c.call_tool("reservar_cita_borrador", {"dni": DNI_OK,
                                                                 "especialidad": "Cardiologia",
                                                                 "celular": celular}))
    assert r.is_error and "999" in r.content[0].text and not carpeta.exists()


def test_propia_especialidad_exige_la_clave_exacta():
    r = correr(lambda c: c.call_tool("cupos_disponibles", {"especialidad": "cardiologia"}))
    assert r.is_error and "Medicina General" in r.content[0].text


def test_propia_borrador_continua_la_numeracion_existente(tmp_path, monkeypatch):
    carpeta = _preparar_raiz(tmp_path, monkeypatch)
    carpeta.mkdir()
    (carpeta / "BORRADOR-07.md").write_text("previo", encoding="utf-8")
    r = correr(lambda c: c.call_tool("reservar_cita_borrador", {"dni": DNI_OK,
                                                                 "especialidad": "Medicina General",
                                                                 "celular": CEL_OK}))
    assert not r.is_error
    assert (carpeta / "BORRADOR-08.md").exists()
    assert (carpeta / "BORRADOR-07.md").read_text(encoding="utf-8") == "previo"   # no pisa archivos previos