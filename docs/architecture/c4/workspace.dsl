workspace "CitaSalud Arequipa" "Modelo C4 del sistema de reserva de citas médicas en centros de salud de Arequipa" {

    !identifiers hierarchical

    model {
        paciente = person "Paciente" "Ciudadano de Arequipa que busca disponibilidad por especialidad, reserva o cancela sus citas médicas."
        admision = person "Personal de admisión" "Personal del centro de salud que administra cupos y registra la asistencia en mostrador."
        medico = person "Médico" "Profesional de salud que consulta su agenda del día y registra la atención de los pacientes."

        citasalud = softwareSystem "CitaSalud Arequipa" "Plataforma regional para consultar disponibilidad de cupos, reservar y cancelar citas médicas con recordatorios automatizados." {
            
            pwa = container "Aplicación web progresiva" "Interfaz web adaptable para pacientes, personal de admisión y médicos [QA-01, QA-02]." "React + Service Worker" "Web Browser"
            
            api = container "API CitaSalud" "Monolito modular con circuit breaker y RLS [QA-01, QA-02, QA-03]." "Python / Django REST Framework" {
                disponibilidad = component "Módulo Disponibilidad y cupos" "Gestiona los cupos de horarios, verifica disponibilidad y busca cupos alternativos." "Django app"
                reservas = component "Módulo Reservas" "Orquesta la creación, confirmación, cancelación y ciclo de vida de las citas." "Django app"
                agenda = component "Módulo Agenda médica" "Administra los centros de salud, médicos, especialidades y agendas diarias." "Django app"
                notificaciones = component "Módulo Notificaciones" "Implementa el adaptador de mensajería para encolar recordatorios hacia WhatsApp." "Django app"
                identidad = component "Módulo Identidad y acceso" "Gestiona la autenticación y el repositorio de pacientes y personal." "Django app"
            }

            worker = container "Worker de recordatorios" "Procesa en segundo plano el envío de recordatorios y sus reintentos." "Celery"
            db = container "Base de datos" "Almacena pacientes, médicos, cupos y citas con aislamiento lógico por esquemas [QA-01, QA-03]." "PostgreSQL 16" "Database"
            cola = container "Cola de tareas y caché" "Almacena las tareas asíncronas de notificación y caché de disponibilidad [QA-01, QA-02]." "Redis" "Queue"
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

        # Relaciones de Nivel 3 (Componentes de la API)
        citasalud.pwa -> citasalud.api.disponibilidad "Consulta cupos disponibles por especialidad" "HTTPS/JSON"
        citasalud.pwa -> citasalud.api.reservas "Solicita reservar o cancelar citas" "HTTPS/JSON"
        citasalud.pwa -> citasalud.api.agenda "Consulta pacientes del día y administra agendas" "HTTPS/JSON"
        citasalud.pwa -> citasalud.api.identidad "Autentica usuarios" "HTTPS/JSON"

        citasalud.api.reservas -> citasalud.api.identidad "Obtiene datos del paciente (RepositorioPacientes)"
        citasalud.api.reservas -> citasalud.api.disponibilidad "Verifica, ocupa o libera cupo y busca alternativos"
        citasalud.api.reservas -> citasalud.api.notificaciones "Solicita programar recordatorio (puerto Notificador)"
        citasalud.api.disponibilidad -> citasalud.api.agenda "Consulta médicos y centros de salud asociados"

        citasalud.api.identidad -> reniec "Valida datos del DNI" "HTTPS/JSON"
        citasalud.api.notificaciones -> citasalud.cola "Encola tarea de envío de WhatsApp" "Redis protocol"

        citasalud.api.reservas -> citasalud.db "Lee y escribe citas (esquema reservas)" "SQL/TCP"
        citasalud.api.disponibilidad -> citasalud.db "Lee y actualiza cupos (esquema disponibilidad)" "SQL/TCP"
        citasalud.api.agenda -> citasalud.db "Lee y escribe médicos y centros (esquema agenda)" "SQL/TCP"
        citasalud.api.identidad -> citasalud.db "Lee y escribe pacientes y usuarios (esquema identidad)" "SQL/TCP"

        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Celular o PC del usuario" "" "Android / navegador web" {
                containerInstance citasalud.pwa
            }
            deploymentNode "VPS en la nube" "" "Ubuntu 24.04 LTS, 2 vCPU, 4 GB RAM" {
                infrastructureNode "Nginx" "Sirve la PWA estática y reenvía /api a Django (ADR-004)." "Nginx"
                containerInstance citasalud.api
                containerInstance citasalud.worker
                containerInstance citasalud.db
                containerInstance citasalud.cola
            }
        }
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

        component citasalud.api "Componentes" "Nivel 3: Componentes internos del contenedor API CitaSalud." {
            include *
            autolayout lr
        }
        deployment citasalud produccion "Despliegue" "Despliegue en producción (MVP)." {
            include *
            autolayout lr
        }

        dynamic citasalud.api "ReservarCita" "Dinámico: reservar una cita verificando cupo y evitando doble asignación." {
            citasalud.pwa -> citasalud.api.reservas "Solicita reservar una cita"
            citasalud.api.reservas -> citasalud.api.identidad "Obtiene datos del paciente"
            citasalud.api.reservas -> citasalud.api.disponibilidad "Verifica y ocupa el cupo"
            citasalud.api.disponibilidad -> citasalud.db "Actualiza el cupo de forma atómica"
            citasalud.api.reservas -> citasalud.db "Registra la cita"
            citasalud.api.reservas -> citasalud.api.notificaciones "Solicita programar recordatorio"
            citasalud.api.notificaciones -> citasalud.cola "Encola tarea de envío de WhatsApp"
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
            element "Component" {
                background #85BBF0
                color #000000
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