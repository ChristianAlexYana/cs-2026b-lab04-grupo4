import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, os
from rendimiento import simular, ESCENARIOS, WORKERS, PRESUPUESTO_P95_MS
nombres = list(ESCENARIOS); vals = [simular(360, WORKERS, f)["p95"] for f in ESCENARIOS.values()]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(nombres, vals, color=["#C8310E", "#C8310E", "#1A3A5C", "#1A3A5C"])
ax.set_yscale("log"); ax.axhline(PRESUPUESTO_P95_MS, color="k", ls="--"); ax.text(3.45, PRESUPUESTO_P95_MS*1.1, "Presupuesto QA-01: 1 s", ha="right")
for i, v in enumerate(vals): ax.text(i, v*1.1, f"{v:,.0f} ms", ha="center")
ax.set_ylabel("p95 (ms, escala log)"); ax.set_title("CitaSalud: p95 a 360 req/s (8x el pico), 8 workers")
plt.tight_layout(); os.makedirs("../docs/architecture/add", exist_ok=True) if False else None
plt.savefig("p95-antes-despues.png", dpi=150)
