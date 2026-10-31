"""Simulación de disponibilidad: caída del servicio de DNI (QA-02).

Compara tres configuraciones durante una caída de 30 minutos:
  A) Sin tácticas
  B) Solo reintentos (ConReintentos)
  C) Reintentos + Circuit Breaker + degradación elegante (reserva pendiente)

SUPUESTOS (no son mediciones de CitaSalud):
  - 45 req/s de reservas en el pico actual (drivers.md)
  - DNI caído 30 min; mientras está caído, cada llamada agota el timeout
  - El breaker se abre tras 5 fallos seguidos y prueba de nuevo cada 30 s
"""
import random

random.seed(42)

CAIDA_S = 30 * 60          # duración de la caída: 30 min
CARGA = 45                 # reservas por segundo (pico actual)
TIMEOUT_S = 2.0            # tiempo que tarda en fallar una llamada al DNI caído
REINTENTOS = 3             # reintentos adicionales en ConReintentos
UMBRAL_BREAKER = 5         # fallos seguidos para abrir el breaker
ESPERA_BREAKER_S = 30      # tiempo abierto antes de probar de nuevo
LATENCIA_OK_S = 0.2        # latencia de una reserva cuando todo va bien
LATENCIA_PENDIENTE_S = 0.15  # reserva pendiente: no espera al DNI


def sin_tacticas():
    perdidas = llamadas = 0
    p95_lat = []
    for _ in range(CAIDA_S * CARGA):
        llamadas += 1
        perdidas += 1                    # la reserva falla
        p95_lat.append(TIMEOUT_S)
    return perdidas, llamadas, p95_lat


def solo_reintentos():
    perdidas = llamadas = 0
    p95_lat = []
    for _ in range(CAIDA_S * CARGA):
        llamadas += 1 + REINTENTOS       # tormenta de reintentos
        perdidas += 1                    # igual falla al final
        p95_lat.append(TIMEOUT_S * (1 + REINTENTOS))
    return perdidas, llamadas, p95_lat


def breaker_y_degradacion():
    perdidas = llamadas = 0
    p95_lat = []
    abierto_hasta = -1
    fallos_seguidos = 0
    for segundo in range(CAIDA_S):
        for _ in range(CARGA):
            if segundo < abierto_hasta:
                # Breaker abierto: no se llama al DNI, reserva pendiente
                p95_lat.append(LATENCIA_PENDIENTE_S)
                continue
            # Breaker cerrado/semiabierto: se intenta llamar al DNI
            llamadas += 1
            fallos_seguidos += 1
            p95_lat.append(TIMEOUT_S + LATENCIA_PENDIENTE_S)
            if fallos_seguidos >= UMBRAL_BREAKER:
                abierto_hasta = segundo + ESPERA_BREAKER_S
                fallos_seguidos = 0
        # ninguna reserva se pierde: queda pendiente de validación
    return perdidas, llamadas, p95_lat


def p95(valores):
    valores = sorted(valores)
    return valores[int(len(valores) * 0.95) - 1]


if __name__ == "__main__":
    total = CAIDA_S * CARGA
    print(f"Caída del DNI: {CAIDA_S // 60} min, carga {CARGA} req/s, "
          f"{total} reservas intentadas\n")
    print(f"{'Configuración':<42}{'Perdidas':>10}{'Llam. DNI':>12}{'p95 (ms)':>10}")
    print("-" * 74)
    for nombre, f in [
        ("A) Sin tácticas", sin_tacticas),
        ("B) Solo reintentos", solo_reintentos),
        ("C) Breaker + reintentos + pendiente", breaker_y_degradacion),
    ]:
        perdidas, llamadas, lat = f()
        print(f"{nombre:<42}{perdidas:>10}{llamadas:>12}{p95(lat) * 1000:>10.0f}")
    print("\nQA-02: 0 reservas perdidas y p95 de reservar <= 2000 ms")