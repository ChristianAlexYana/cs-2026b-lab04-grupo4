# ADR-006: Patrones de diseño en el módulo Reservas

- Estado: Aceptado
- Fecha: 2026-10-25
- Decisores: Yana Huanca Christian Alexander, Estrada Arce Sergio Emilio y Mamani Quispe Renzo Geomar

## Contexto
La versión ingenua de `reservar_cita()` (`src/reservas/antes/servicio.py`) concentraba en un solo método la validación de estado, la validación de DNI, la búsqueda de cupo por política, los reintentos de notificación y el conocimiento de los SDK de WhatsApp y DNI. Su complejidad ciclomática medida con radon es C (14) y el promedio del módulo es B (5.4). Los olores detectados (ver `docs/design/patrones/olores.md`) fueron: if/elif por política de cupos, dependencia directa de SDK externos, condicionales anidados sobre el estado de la cita, notificación armada a mano y un bloque de reintentos duplicado. Además, el caso incluye una función de IA no determinista (sugerir la especialidad según el motivo de consulta, sin diagnosticar), cuya salida no es confiable. El MVP debe estar en producción en 1 mes con 3 developers, por lo que solo se aplican patrones que un olor concreto justifique (ADR-001, ADR-005).

## Alternativas consideradas
1. **Dejar la versión «antes».** 48 líneas en un archivo y sin indirección, pero cada política, canal o estado nuevo obliga a editar `reservar_cita()`.
2. **Aplicar patrones solo donde hay un olor y una prueba que lo demuestre** (Strategy + Adapter + Factory, State, Observer, Decorator y Chain of Responsibility).
3. **Singleton para las fábricas** (propuesto por la IA). Se rechazó: introduce estado global y dificulta inyectar dependencias en las pruebas.
4. **Aplicar todos los patrones del catálogo «por si acaso».** Se rechazó por patternitis: más clases sin un olor que lo justifique y sin tiempo en el plazo del MVP.

## Decisión
Usaremos la alternativa 2:
- **Strategy + Factory** (`politicas.py`) para la política de asignación de cupos alternativos.
- **Adapter** (`adaptadores.py`) para WhatsApp y el servicio de DNI, detrás de los puertos `Notificador` (ADR-005) y `ValidadorIdentidad`.
- **State** (`estados.py`) para el ciclo de vida de la cita.
- **Observer** (`eventos.py`) para publicar `CITA_RESERVADA` a varios suscriptores, y **Decorator** (`ConReintentos`) que reintenta solo ante `TimeoutError` (ADR-003).
- **IA aislada** (`ia.py`): `ProveedorLLM` con adaptador, **Decorator** de caché y de guardrails, y **Chain of Responsibility** (`LongitudMaxima` → `SinDiagnosticos` → `EspecialidadValida`). La respuesta del LLM se trata como dato no confiable y las pruebas usan un LLM simulado, sin claves ni red.
No se usará Singleton. Cada patrón tiene una prueba en `tests/test_patrones.py` y las pruebas de comportamiento corren sobre `antes` y `despues` (28 pruebas en verde).

## Consecuencias
Positivas: `reservar_cita()` baja de C (14) a A (3) y el promedio del módulo de B (5.4) a A (3.2); agregar una política, un suscriptor o un proveedor de IA no obliga a modificar el servicio (abierto/cerrado); cada responsabilidad se prueba por separado; el componente de IA es sustituible y probable sin claves de API.
Negativas / riesgos: el SLOC sube de 48 a 159 y de 1 archivo a 5; seguir el flujo exige saltar entre módulos (`eventos`, `politicas`, `estados`, `adaptadores`); la IA puede cambiar reglas en silencio (por ejemplo, reintentar ante cualquier excepción), por lo que las pruebas de caracterización son obligatorias antes de aceptar sus refactors. El State implementa 3 de los 5 estados del Lab 05; CONFIRMADA, ATENDIDA y NO_ASISTIO quedan pendientes.
