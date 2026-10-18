# Revisión con la lista oficial de C4 — CitaSalud Arequipa

Se aplicó la lista de revisión de c4model.com (Tabla 3 de la guía: General, Elementos y Relaciones) a las cinco imágenes de `img/` y a los `.puml` de `export/`. El `workspace.dsl` pasa `structurizr validate` sin errores.

| Vista | General (título, alcance, leyenda) | Elementos (nombre, tipo, descripción, tecnología) | Relaciones (etiqueta, dirección, protocolo) | Evidencia y observaciones |
|-------|-----------------------------------|---------------------------------------------------|---------------------------------------------|---------------------------|
| Contexto | Sí | **No del todo** | Sí | Título "Nivel 1", leyenda presente. En el PNG de C4-PlantUML los 2 sistemas externos salen del mismo azul que CitaSalud y la leyenda no distingue "externo" (el export no usa `System_Ext`). En Structurizr Lite y en el export Mermaid sí salen en gris. Las flechas de las personas no llevan protocolo: a nivel 1 no se exige |
| Contenedores | Sí | **No del todo** | Sí | Cada contenedor tiene tecnología y cada flecha su protocolo. Misma limitación: WhatsApp y DNI salen azules como un sistema propio. La etiqueta "Valida identidad del paciente" queda cerca de otra flecha |
| Componentes | Sí | Sí | Sí | 5 módulos "Django app" que coinciden con paquetes.puml; no hay ciclos (Reservas → Identidad, Disponibilidad, Notificaciones; Disponibilidad → Agenda). Hay muchas flechas cruzadas pero todas tienen etiqueta y protocolo |
| Dinámica | Sí | Sí | Sí | 7 pasos numerados; cada paso es una relación que ya existe en el modelo |
| Despliegue | Sí | Sí | **No** | Nodos con SO y tamaño; 5 instancias de contenedor. Pero Nginx aparece suelto, sin flechas: la flecha PWA → API no pasa por él, aunque la descripción de Nginx dice que reenvía `/api` a Django (ADR-004). No se muestra un entorno de ejecución (p. ej. Docker) dentro del VPS |

## Hallazgos del segundo revisor (Prompt IA 2, Claude)

| Vista | Hallazgo de la IA | Verificación del equipo |
|-------|-------------------|-------------------------|
| Contexto | Las 3 relaciones de las personas con CitaSalud no indican tecnología ni protocolo | **Falso positivo.** En el nivel 1 no se exigen tecnologías para las personas ni para el sistema |
| Contexto y Contenedores | Los sistemas externos no se distinguen de los internos en el PNG | Correcto. Es una limitación del export a C4-PlantUML (etiqueta `Externo` con `$tags=""`). Se documenta; el export Mermaid y Structurizr Lite sí los muestran en gris |
| Despliegue | Nginx no está conectado con nada | Correcto. Falta modelar PWA → Nginx → API en `workspace.dsl` |
| Componentes | Hay un ciclo entre Reservas y Notificaciones | **Falso positivo.** Solo existe la flecha Reservas → Notificaciones; Notificaciones solo escribe en la cola |
| Todas | Todas tienen título, descripción y leyenda | Correcto (cumple) |
