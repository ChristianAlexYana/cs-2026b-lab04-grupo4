workspace "CitaSalud Arequipa" "Modelo C4 del sistema de reserva de citas médicas en centros de salud de Arequipa" {

    !identifiers hierarchical

    model {
        paciente = person "Paciente" "Ciudadano de Arequipa que busca disponibilidad por especialidad, reserva o cancela sus citas médicas."
        admision = person "Personal de admisión" "Personal del centro de salud que administra cupos y registra la asistencia en mostrador."
        medico = person "Médico" "Profesional de salud que consulta su agenda del día y registra la atención de los pacientes."

        citasalud = softwareSystem "CitaSalud Arequipa" "Plataforma regional para consultar disponibilidad de cupos, reservar y cancelar citas médicas con recordatorios automatizados." {
            pwa = container "Aplicación web progresiva" "Interfaz web adaptable para pacientes, personal de admisión y médicos." "React + Service Worker" "Web Browser"
            api = container "API CitaSalud" "Monolito modular que expone la lógica de negocio mediante una API REST." "Python / Django REST Framework"
            worker = container "Worker de recordatorios" "Procesa en segundo plano el envío de recordatorios y sus reintentos." "Celery"
            db = container "Base de datos" "Almacena pacientes, médicos, cupos y citas con aislamiento lógico por esquemas." "PostgreSQL 16" "Database"
            cola = container "Cola de tareas y caché" "Almacena las tareas asíncronas de notificación y caché de disponibilidad." "Redis" "Queue"
        }

        whatsapp = softwareSystem "WhatsApp Business API" "Servicio externo de mensajería para el envío de confirmaciones y recordatorios de citas." "Externo"
        reniec = softwareSystem "Servicio de consulta de DNI" "Servicio externo para validar los datos básicos de identificación del ciudadano." "Externo"

        # Relaciones de Nivel 1 (Contexto)
        paciente -> citasalud "Consulta disponibilidad, reserva y cancela citas"
        admision -> citasalud "Administra cupos de atención y recepciona pacientes"
        medico -> citasalud "Consulta la lista de pacientes del día y registra atenciones"
        citasalud -> whatsapp "Envía recordatorios y avisos de citas" "HTTPS/JSON"
        citasalud -> reniec "Consulta datos básicos de identidad por DNI" "HTTPS/JSON"

        # Relaciones de Nivel 2 (Contenedores)
        paciente -> citasalud.pwa "Reserva y cancela citas desde su navegador" "HTTPS"
        admision -> citasalud.pwa "Gestiona cupos y admisión del día" "HTTPS"
        medico -> citasalud.pwa "Consulta agenda diaria y registra atención" "HTTPS"

        citasalud.pwa -> citasalud.api "Realiza peticiones a la API" "HTTPS/JSON (REST)"
        citasalud.api -> citasalud.db "Lee y escribe registros transaccionales" "SQL/TCP"
        citasalud.api -> citasalud.cola "Encola tareas de recordatorio y consulta caché" "Redis protocol"
        citasalud.api -> reniec "Valida identidad del paciente" "HTTPS/JSON"
        citasalud.worker -> citasalud.cola "Consume tareas de envío programadas" "Redis protocol"
        citasalud.worker -> whatsapp "Despacha mensajes de recordatorio" "HTTPS/JSON"
    }

    views {
        systemContext citasalud "Contexto" "Nivel 1: Diagrama de contexto del sistema CitaSalud Arequipa." {
            include *
            autolayout lr
        }

        container citasalud "Contenedores" "Nivel 2: Contenedores que conforman CitaSalud Arequipa." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}