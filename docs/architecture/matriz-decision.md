# Matriz de decisión — CitaSalud Arequipa

## Alternativas
- **A. Monolito en capas:** una sola aplicación con capas presentación, lógica de negocio y acceso a datos, y una base de datos. Es la más simple, pero sin límites internos por dominio.
- **B. Monolito modular:** un solo despliegue dividido en módulos (Disponibilidad, Reservas, Agenda médica, Notificaciones, Identidad) que se comunican por interfaces públicas; una BD con esquema por módulo.
- **C. Microservicios:** un servicio por dominio, cada uno con su BD, API Gateway y broker de eventos; se despliegan y escalan por separado.

## Criterios y pesos (suman 100 %)
| Criterio                          | Peso | Justificación (driver relacionado)                                              |
|-----------------------------------|------|---------------------------------------------------------------------------------|
| Tiempo de entrega                 | 25 % | R-01: el MVP debe salir en 1 mes                                                |
| Integridad de citas (consistencia)| 20 % | QA-02: ninguna cita asignada dos veces; es el riesgo más grave del dominio      |
| Modificabilidad                   | 20 % | Atributo 4: nuevos canales de recordatorio y reglas por centro de salud         |
| Simplicidad operativa             | 15 % | R-02: 3 developers sin equipo de operaciones                                    |
| Costo operativo                   | 10 % | R-03: un VPS de bajo costo                                                      |
| Escalabilidad                     | 10 % | QA-01: pico de 5000 pacientes en 15 min, pero corto y predecible (7:00–7:15)    |

## Matriz (puntaje 1 = muy malo … 5 = excelente)
| Criterio (peso)                    | A. Capas | B. Monolito modular | C. Microservicios |
|------------------------------------|------|------|------|
| Tiempo de entrega (25 %)           | 5    | 4    | 2    |
| Integridad de citas (20 %)         | 5    | 5    | 2    |
| Modificabilidad (20 %)             | 2    | 4    | 5    |
| Simplicidad operativa (15 %)       | 5    | 4    | 1    |
| Costo operativo (10 %)             | 5    | 5    | 2    |
| Escalabilidad (10 %)               | 2    | 3    | 5    |
| **Total ponderado**                | **4,10** | **4,20** | **2,75** |

Total ponderado = Σ (peso × puntaje). Ejemplo B: 0,25×4 + 0,20×5 + 0,20×4 + 0,15×4 + 0,10×5 + 0,10×3 = 4,20.

Justificación de puntajes clave: en A y B la reserva ocurre en una sola transacción de PostgreSQL (integridad = 5); en C la reserva cruza servicios y requiere consistencia eventual (integridad = 2); C exige 5 despliegues, varias BD y un broker para 3 developers (simplicidad = 1).

## Análisis de sensibilidad
La diferencia entre B (4,20) y A (4,10) es pequeña. B gana por modificabilidad (20 %); si ese peso bajara a 10 % y el de simplicidad subiera a 25 %, A pasaría a ganar. Por eso el equipo debe defender el peso de modificabilidad con el driver del atributo 4, no ajustarlo para obtener un resultado. **[El equipo debe confirmar o cambiar estos pesos y puntajes según su propio criterio.]**

## Conclusión
Elegimos **B. Monolito modular** porque cumple el plazo de 1 mes (R-01), garantiza la integridad de las citas con transacciones de una sola BD (QA-02) y deja los módulos separados para agregar canales sin tocar el resto. Ver [ADR-001](adr/001-estilo-arquitectonico.md).
