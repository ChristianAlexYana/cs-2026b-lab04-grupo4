"""Simulación de cola M/G/c del pico de las 7:00 a. m. en CitaSalud (QA-01).

Llegan consultas de disponibilidad (Poisson) y las atienden `workers` procesos del
monolito (ADR-001) en un solo VPS. Se compara el p95 con distintas tácticas.
SUPUESTOS (validar con medición real; ver add/iteracion-1.md):
  - 8 workers en el VPS; consulta de disponibilidad sin índice ~90 ms, con índice ~30 ms.
  - Caché de disponibilidad con 85 % de aciertos; un acierto cuesta ~5 ms.
  - Pico actual 45 req/s (drivers.md: 40-50); con 8x = 360 req/s.
"""
import heapq, math, random, statistics

PRESUPUESTO_P95_MS = 1000   # QA-01
WORKERS = 8

def simular(lam, workers, servicio, segundos=60, semilla=7):
    rnd = random.Random(semilla)
    t, llegadas = 0.0, []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)
    libres = [0.0] * workers
    heapq.heapify(libres)
    resp = []
    for a in llegadas:
        libre = heapq.heappop(libres)
        fin = max(a, libre) + servicio(rnd)
        heapq.heappush(libres, fin)
        resp.append((fin - a) * 1000)
    resp.sort()
    p = lambda q: resp[int(q * (len(resp) - 1))]
    return {"n": len(resp), "p50": p(0.50), "p95": p(0.95), "media": statistics.mean(resp)}

def ln(media_s, sigma):             # lognormal con la media dada
    return lambda r: r.lognormvariate(math.log(media_s) - sigma ** 2 / 2, sigma)

bd_sin_indice = ln(0.090, 0.45)
bd_con_indice = ln(0.030, 0.40)
acierto = ln(0.005, 0.30)
def con_cache(base, p=0.85):
    return lambda r: acierto(r) if r.random() < p else base(r)

CARGAS = [("normal (5 req/s)", 5), ("pico actual (45 req/s)", 45), ("pico 8x (360 req/s)", 360)]
ESCENARIOS = {
    "Sin tácticas":          bd_sin_indice,
    "Índice en BD":          bd_con_indice,
    "Caché (85 % aciertos)": con_cache(bd_sin_indice),
    "Índice + caché":        con_cache(bd_con_indice),
}

if __name__ == "__main__":
    for carga, lam in CARGAS:
        print(f"\nCarga {carga}, {WORKERS} workers")
        for nombre, f in ESCENARIOS.items():
            r = simular(lam, WORKERS, f)
            ok = "CUMPLE" if r["p95"] <= PRESUPUESTO_P95_MS else "NO cumple"
            print(f"  {nombre:24s} p50={r['p50']:8.0f} ms  p95={r['p95']:8.0f} ms  {ok}")
