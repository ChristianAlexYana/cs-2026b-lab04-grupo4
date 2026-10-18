# Comparación

## E4: vista dinámica frente a secuencia UML

La secuencia UML del Lab 05 muestra lo que la vista dinámica omite: el orden estricto de los mensajes entre objetos, los mensajes de retorno y los fragmentos condicionales, como la rama `alt` en que el cupo ya está ocupado y se ofrecen cupos alternativos (CA-2, respuesta 409). La vista dinámica solo numera interacciones entre contenedores y componentes sobre el mismo modelo, sin condiciones ni retornos. La secuencia sirve a los developers que implementan y prueban la lógica; la vista dinámica sirve al equipo técnico y a operaciones para ver qué partes colaboran en un flujo crítico y se mantiene sincronizada con las demás vistas.

## E6: escrito a mano (contexto-manual.puml) frente a modelo exportado (workspace.dsl)

| Criterio | Escrito a mano (contexto-manual.puml) | Modelo exportado (workspace.dsl) |
|---|---|---|
| Tiempo invertido | ≈6 min para un solo diagrama (el de contexto; archivo creado a las 01:31 y renderizado a las 01:37); cada vista adicional exigiría otro archivo escrito a mano. | ≈3 min de ejecución efectiva para exportar a C4-PlantUML y Mermaid y generar los 5 PNG (exportación a las 01:24 y PNG a las 01:27), a partir del modelo ya existente. El proceso total tomó ≈1 h 54 min desde el primer intento (23:33) por el desvío del CLI antiguo. |
| Errores encontrados | Ninguno detectado al escribirlo. Sin embargo, nada comprueba automáticamente que los nombres y las etiquetas coincidan con el modelo: una diferencia habría pasado inadvertida. | El Structurizr CLI antiguo (`structurizr/cli`) no exportó ningún archivo y solo mostró un aviso de que ya no recibe actualizaciones, sin indicar error. Se resolvió migrando a la imagen `structurizr/structurizr`, con las opciones `-workspace`, `-format` y `-output`. |
| Si mañana cambia el nombre de un contenedor | Hay que corregirlo a mano en cada diagrama que lo mencione; es fácil olvidar alguno. | Se cambia una vez en `workspace.dsl` y al volver a exportar todas las vistas se actualizan. |

## Conclusión

Escribir un diagrama a mano es rápido para una sola vista, pero no escala: cada vista es un archivo independiente que puede quedar desactualizado. Modelar con Structurizr DSL requiere más preparación inicial (herramientas y comandos), pero las 5 vistas salen de un único modelo y se mantienen coherentes.