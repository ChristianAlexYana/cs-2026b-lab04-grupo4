"""Grafica las tasas reales de promptfoo sin depender de matplotlib."""

import json
import subprocess
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
datos = json.loads((RAIZ / "resultados.json").read_text(encoding="utf-8"))
prompts = datos["results"]["prompts"]
versiones = ["v1", "v2", "v3", "v3.1"]
colores = ["#64748b", "#f59e0b", "#3b82f6", "#16a34a"]
metricas = {}
for p in prompts:
    nombre = p["label"].split(".txt", 1)[0]
    metricas[nombre] = p["metrics"]

assert set(versiones) == set(metricas), "Faltan versiones en resultados.json"

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1250" height="760" viewBox="0 0 1250 760">',
       '<rect width="1250" height="760" fill="white"/>',
       '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#172554} .titulo{font-size:23px;font-weight:bold} .etiqueta{font-size:14px} .dato{font-size:13px}</style>',
       '<text x="50" y="47" class="titulo">CitaSalud: aprobación por versión y aserción</text>',
       '<text x="50" y="78" class="etiqueta">Tasa de casos que superan todas las aserciones</text>']

for i, version in enumerate(versiones):
    m = metricas[version]
    aprobados = m["testPassCount"]
    total = aprobados + m["testFailCount"] + m["testErrorCount"]
    tasa = 100 * aprobados / total
    y = 105 + i * 48
    svg += [f'<text x="50" y="{y+22}" class="etiqueta">{version}</text>',
            f'<rect x="105" y="{y}" width="{tasa*8:.1f}" height="30" fill="{colores[i]}"/>',
            f'<text x="{115+tasa*8:.1f}" y="{y+21}" class="dato">{aprobados}/{total} ({tasa:g}%)</text>']

svg.append('<text x="50" y="330" class="etiqueta">Aprobación por aserción (denominador según los casos donde aplica)</text>')
aserciones = ["A1_contrato_json", "A2_exito_y_error", "A3_sin_implementacion",
              "A4_rechaza_no_invest", "A5_resiste_inyeccion", "A6_espanol", "A7_sin_datos_personales"]
for j, nombre in enumerate(aserciones):
    y = 360 + j * 48
    svg.append(f'<text x="50" y="{y+18}" class="etiqueta">{nombre}</text>')
    for i, version in enumerate(versiones):
        m = metricas[version]
        ok = m["namedScores"][nombre]
        total = m["namedScoresCount"][nombre]
        tasa = 100 * ok / total
        x = 310 + i * 225
        svg += [f'<rect x="{x}" y="{y}" width="{tasa*1.25:.1f}" height="23" fill="{colores[i]}"/>',
                f'<text x="{x+130}" y="{y+17}" class="dato">{ok}/{total}</text>']
for i, version in enumerate(versiones):
    svg.append(f'<text x="{310+i*225}" y="730" class="etiqueta">{version}</text>')
svg.append('</svg>')
subprocess.run(["rsvg-convert", "-o", str(RAIZ / "resultados.png")],
               input="\n".join(svg), text=True, check=True)
