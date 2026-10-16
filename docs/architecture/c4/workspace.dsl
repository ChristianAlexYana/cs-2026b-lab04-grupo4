workspace "CitaSalud Arequipa" "Modelo C4 del sistema de reserva de citas médicas en centros de salud de Arequipa" {

    !identifiers hierarchical

    model {
        paciente = person "Paciente" "Ciudadano de Arequipa que busca disponibilidad por especialidad, reserva o cancela sus citas médicas."
        admision = person "Personal de admisión" "Personal del centro de salud que administra cupos y registra la asistencia en mostrador."
        medico = person "Médico" "Profesional de salud que consulta su agenda del día y registra la atención de los pacientes."

        citasalud = softwareSystem "CitaSalud Arequipa" "Plataforma regional para consultar disponibilidad de cupos, reservar y cancelar citas médicas con recordatorios automatizados."

        whatsapp = softwareSystem "WhatsApp Business API" "Servicio externo de mensajería para el envío de confirmaciones y recordatorios de citas." "Externo"
        reniec = softwareSystem "Servicio de consulta de DNI" "Servicio externo para validar los datos básicos de identificación del ciudadano." "Externo"

        # Relaciones de Nivel 1 (Contexto)
        paciente -> citasalud "Consulta disponibilidad, reserva y cancela citas"
        admision -> citasalud "Administra cupos de atención y recepciona pacientes"
        medico -> citasalud "Consulta la lista de pacientes del día y registra atenciones"
        citasalud -> whatsapp "Envía recordatorios y avisos de citas" "HTTPS/JSON"
        citasalud -> reniec "Consulta datos básicos de identidad por DNI" "HTTPS/JSON"
    }

    views {
        systemContext citasalud "Contexto" "Nivel 1: Diagrama de contexto del sistema CitaSalud Arequipa." {
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
        }
    }
}