# Iteración 1 de ADD: rendimiento en el pico de las 7:00 a. m. (QA-01)

## Paso 1. Drivers
Escenario QA-01 (H,M): 360 req/s a las 7:00 (8x el pico actual de 45 req/s, `drivers.md`) -> p95 de la consulta de disponibilidad <= 1 s.
Restricciones: 1 VPS, ADR-001 (monolito modular).

## Paso 2. Elemento a refinar
Módulo Reservas (consulta de disponibilidad) dentro del monolito.

## Paso 3. Concepto de diseño (tácticas candidatas, Prompt IA 2)
| Táctica | Propuesta de la IA | Decisión |
|---|---|---|
| Caché de disponibilidad | Reduce lecturas a la BD; riesgo de datos desactualizados | ADOPTADA |
| Índice en BD | Baja el costo por consulta | ADOPTADA (complemento) |
| Separar Reservas en un microservicio | Escala aparte | RECHAZADA: no hay evidencia de que el cuello sea el monolito; sube la complejidad y el costo con 1 VPS y 1 mes |
| ... | ... | COMPLETAR con lo que respondió realmente la IA |

## Paso 4-5. Instanciación y vistas
Caché en memoria/Redis delante de `consultar_disponibilidad`; TTL corto y se invalida al reservar o cancelar. COMPLETAR: contenedor C4 si se agrega Redis.

## Paso 6-7. Evidencia (`fitness/rendimiento.py`, 8 workers, 60 s simulados)
| Carga | Sin tácticas | Índice | Caché 85 % | Índice + caché |
|---|---|---|---|---|
| 45 req/s | 170 ms | 52 ms | 98 ms | 33 ms |
| 360 req/s | 176 083 ms (colapsa) | 20 790 ms (colapsa) | 120 ms | 33 ms |

Conclusión: el índice solo NO alcanza a 360 req/s; la caché es la táctica decisiva y el índice la complementa. Con ambas se cumple QA-01 con margen.

## Supuestos (si fallan, la decisión cambia)
- Consulta sin índice ~90 ms, con índice ~30 ms, acierto de caché ~5 ms (NO medidos: COMPLETAR con medición real).
- 85 % de aciertos: depende de que las consultas se repitan por establecimiento y especialidad.
- 8 workers en un VPS; pico de 360 req/s derivado de drivers.md.
- Trade-off aceptado: datos de disponibilidad con hasta TTL segundos de antigüedad; la reserva real valida contra la BD.
