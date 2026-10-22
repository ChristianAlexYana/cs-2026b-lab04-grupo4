from src.reservas.externos import WhatsAppSDK, ReniecSDK

class Cita:
    def __init__(self, id, paciente_dni, celular, especialidad, estado="BORRADOR"):
        self.id = id
        self.paciente_dni = paciente_dni
        self.celular = celular
        self.especialidad = especialidad
        self.estado = estado
        self.cupo_ocupado = False

class ServicioReservasAntes:
    def __init__(self, reniec_sdk=ReniecSDK(), wa_sdk=WhatsAppSDK()):
        self.reniec = reniec_sdk
        self.wa = wa_sdk
        self.eventos = []
        self.cupos_db = {"Medicina General": True, "Cardiologia": False} # Simulación BD

    def reservar_cita(self, cita: Cita, politica_alternativos: str = "PRONTO") -> str:
        # OLOR 1: Condicionales sobre estado (Pide patrón State)
        if cita.estado != "BORRADOR":
            if cita.estado == "RESERVADA":
                raise ValueError("La cita ya está reservada")
            elif cita.estado == "CANCELADA":
                raise ValueError("La cita está cancelada")
            else:
                raise ValueError("Estado no válido")

        # OLOR 2: Conoce detalles del SDK externo (Pide patrón Adapter)
        codigo, datos = self.reniec.consultar(cita.paciente_dni)
        if codigo != 200 or not datos.get("valido"):
            raise ValueError("DNI inválido")

        disponible = self.cupos_db.get(cita.especialidad, False)
        
        # OLOR 3: if/elif que crece con cada política (Pide Strategy + Factory)
        if not disponible:
            if politica_alternativos == "PRONTO":
                disponible = True # Simula que encontró el más pronto
            elif politica_alternativos == "MISMO_MEDICO":
                disponible = False # Simula que el médico no tiene cupo
            else:
                raise ValueError(f"Política no soportada: {politica_alternativos}")
            
            if not disponible:
                raise ValueError("No hay cupos alternativos")

        cita.cupo_ocupado = True
        cita.estado = "RESERVADA"

        # OLOR 4: Reintentos duplicados y notificaciones a mano (Pide Decorator y Observer)
        for intento in range(3):
            try:
                res = self.wa.enviar_mensaje(cita.celular, f"Cita {cita.id} reservada")
                if res.get("ok"):
                    self.eventos.append(f"whatsapp: {cita.celular}: Cita {cita.id} reservada")
                    break
            except TimeoutError:
                if intento == 2:
                    raise ValueError("Error de red al notificar")

        return cita.estado