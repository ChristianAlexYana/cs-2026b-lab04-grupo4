"""Lee el resultados.json de promptfoo: imprime la tabla de tasas, dibuja los gráficos y
actúa como compuerta de calidad (la regla de oro: sin evidencia no hay prompt nuevo).

    python prompts/graficar_resultados.py prompts/criterios/resultados.json
    python prompts/graficar_resultados.py prompts/criterios/resultados.json --version v3 --minimo 85 --sin-graficos

Salida: tabla en Markdown (para el README), img/tasa_por_version.png e img/heatmap.png
junto al resultados.json. Termina con código 1 si la versión elegida no llega al mínimo.
Requiere: pip install matplotlib
"""
import argparse
import collections
import json
import pathlib
import re
import sys


def clave_version(v):
    return [int(x) for x in v[1:].split(".")]


def leer(ruta):
    datos = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    ok = collections.defaultdict(dict)          # version -> caso -> pasó todo
    fallas = collections.defaultdict(dict)      # version -> caso -> aserciones que fallaron
    por_asercion = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for r in datos["results"]["results"]:
        m = re.match(r"\s*(?:file://)?(?:[^\s:]*/)?(v\d+(?:\.\d+)*)\.txt", r["prompt"]["label"])
        v, caso = m.group(1), r["vars"]["id"]
        ok[v][caso] = bool(r["success"])
        fallas[v][caso] = []
        for c in (r.get("gradingResult") or {}).get("componentResults", []):
            nombre = (c.get("assertion") or {}).get("metric") or "sin_nombre"
            por_asercion[v][nombre][1] += 1
            por_asercion[v][nombre][0] += bool(c["pass"])
            if not c["pass"]:
                fallas[v][caso].append(nombre.split("_")[0])
    return ok, fallas, por_asercion


def tabla(ok):
    filas = ["| Versión | Casos aprobados | Tasa |", "|---|---|---|"]
    for v in sorted(ok, key=clave_version):
        p, t = sum(ok[v].values()), len(ok[v])
        filas.append(f"| {v} | {p}/{t} | {100 * p / t:.1f} % |")
    return "\n".join(filas)


def graficos(ok, fallas, carpeta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    carpeta.mkdir(parents=True, exist_ok=True)
    vs = sorted(ok, key=clave_version)
    casos = sorted({c for v in vs for c in ok[v]}, key=lambda c: (len(c), c))

    fig, ax = plt.subplots(figsize=(6.5, 4))
    tasas = [100 * sum(ok[v].values()) / len(ok[v]) for v in vs]
    barras = ax.bar(vs, tasas, color="#2E75B6")
    for b, v, t in zip(barras, vs, tasas):
        ax.text(b.get_x() + b.get_width() / 2, t + 2, f"{t:.1f} %\n({sum(ok[v].values())}/{len(ok[v])})",
                ha="center", fontsize=9, weight="bold")
    ax.axhline(85, color="#C8310E", ls="--", lw=1)
    ax.text(len(vs) - 0.5, 86, "meta 85 %", color="#C8310E", ha="right", fontsize=8)
    ax.set(ylim=(0, 120), ylabel="Casos que pasan TODAS las aserciones (%)", title="Tasa de aprobación por versión")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(carpeta / "tasa_por_version.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(1.6 * len(vs) + 3, 0.5 * len(casos) + 1.5))
    z = [[1 if ok[v].get(c) else 0 for v in vs] for c in casos]
    ax.imshow(z, cmap=ListedColormap(["#F4CCC3", "#D9EAD3"]), aspect="auto", vmin=0, vmax=1)
    for i, c in enumerate(casos):
        for j, v in enumerate(vs):
            txt = "✓" if z[i][j] else "✗ " + ", ".join(fallas[v].get(c, []))
            ax.text(j, i, txt, ha="center", va="center", fontsize=9, color="#1E7B34" if z[i][j] else "#C8310E")
    ax.set_xticks(range(len(vs)), vs)
    ax.set_yticks(range(len(casos)), casos)
    ax.set_title("Resultado por caso (✗ indica las aserciones que fallaron)")
    fig.tight_layout()
    fig.savefig(carpeta / "heatmap.png", dpi=180)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("resultados")
    ap.add_argument("--version", help="versión a controlar (por defecto, la más reciente)")
    ap.add_argument("--minimo", type=float, help="tasa mínima (%%) que debe alcanzar esa versión")
    ap.add_argument("--sin-graficos", action="store_true")
    a = ap.parse_args()

    ok, fallas, _ = leer(a.resultados)
    print(tabla(ok))
    if not a.sin_graficos:
        graficos(ok, fallas, pathlib.Path(a.resultados).parent / "img")
        print("\nGráficos en", pathlib.Path(a.resultados).parent / "img")
    if a.minimo is not None:
        v = a.version or max(ok, key=clave_version)
        tasa = 100 * sum(ok[v].values()) / len(ok[v])
        if tasa < a.minimo:
            print(f"\nFALLA: {v} tiene {tasa:.1f} % y la meta es {a.minimo:.0f} %")
            for c, f in fallas[v].items():
                if f:
                    print(f"  - {v}/{c}: fallaron {', '.join(f)}")
            return 1
        print(f"\nOK: {v} tiene {tasa:.1f} % (meta {a.minimo:.0f} %)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
