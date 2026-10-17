# Comparación

## E4: vista dinámica frente a secuencia UML

La secuencia UML del Lab 05 muestra lo que la vista dinámica omite: el orden estricto de los mensajes entre objetos, los mensajes de retorno y los fragmentos condicionales, como la rama `alt` en que el cupo ya está ocupado y se ofrecen cupos alternativos (CA-2, respuesta 409). La vista dinámica solo numera interacciones entre contenedores y componentes sobre el mismo modelo, sin condiciones ni retornos. La secuencia sirve a los developers que implementan y prueban la lógica; la vista dinámica sirve al equipo técnico y a operaciones para ver qué partes colaboran en un flujo crítico y se mantiene sincronizada con las demás vistas.

## E6: escrito a mano (contexto-manual.puml) frente a modelo exportado (workspace.dsl)

| Criterio | Escrito a mano (contexto-manual.puml) | Modelo exportado (workspace.dsl) |
|---|---|---|
| Tiempo invertido | X min para un solo diagrama (el de contexto); cada vista adicional exigiría otro archivo escrito a mano. | Y min para validar, exportar a C4-PlantUML y Mermaid y generar los 5 PNG; las 5 vistas salen con comandos a partir del modelo ya existente. |
| Errores encontrados | Ninguno detectado al escribirlo. Sin embargo, nada comprueba automáticamente que los nombres y las etiquetas coincidan con el modelo: una diferencia habría pasado inadvertida. | El Structurizr CLI antiguo (`structurizr/cli`) no exportó ningún archivo y solo mostró un aviso de que ya no recibe actualizaciones, sin indicar error. Se resolvió migrando a la imagen `structurizr/structurizr`, con las opciones `-workspace`, `-format` y `-output`. |
| Si mañana cambia el nombre de un contenedor | Hay que corregirlo a mano en cada diagrama que lo mencione; es fácil olvidar alguno. | Se cambia una vez en `workspace.dsl` y al volver a exportar todas las vistas se actualizan. |

## Conclusión

Escribir un diagrama a mano es rápido para una sola vista, pero no escala: cada vista es un archivo independiente que puede quedar desactualizado. Modelar con Structurizr DSL requiere más preparación inicial (herramientas y comandos), pero las 5 vistas salen de un único modelo y se mantienen coherentes.