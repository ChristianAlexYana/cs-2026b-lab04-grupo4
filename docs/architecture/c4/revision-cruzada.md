# Revisión cruzada — diagrama de contenedores de RutaSIT Arequipa (Grupo 06)

Revisado por el Grupo 04 (CitaSalud Arequipa) con la lista oficial de c4model.com. Repositorio revisado: https://github.com/R0otDrigo/cs-2026b-lab04-grupo06

| Grupo | Pregunta de la lista | ¿Cumple? | Observación |
|-------|----------------------|----------|-------------|
| General | ¿Tiene título y se entiende el alcance? | Parcial | La imagen dice solo "RutaSIT - Containers". La vista del DSL tiene la descripción "Nivel 2: contenedores de RutaSIT", pero no aparece en la imagen |
| General | ¿Tiene leyenda? | No | La imagen de contenedores no incluye leyenda (persona, sistema externo, contenedor, base de datos). Se puede agregar al exportar |
| Elementos | ¿Nombre, tipo, descripción y tecnología? | Sí | Los 4 contenedores indican tecnología (JavaScript + Service Worker, Python / Django, PostgreSQL + PostGIS, Redis) y los externos salen en gris |
| Relaciones | ¿Etiqueta con intención y protocolo? | Parcial | Todas tienen protocolo. Las de las personas dicen solo "Usa"; un verbo más específico ("Consulta buses y llegadas") comunicaría mejor la intención. La etiqueta "Carga los mapas" queda sobre la línea y cuesta leerla |
| Relaciones | ¿La dirección coincide con la etiqueta? | Sí | Las flechas de GPS → API y API → Proveedor de mapas son coherentes |

Fortalezas: contenedores coherentes con su ADR-001 (monolito modular, sin Docker ni Nginx como contenedores) y protocolos en todas las flechas entre contenedores.
