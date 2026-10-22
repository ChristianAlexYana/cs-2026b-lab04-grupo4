class WhatsAppSDK:
    def enviar_mensaje(self, telefono: str, texto: str) -> dict:
        return {"ok": True, "id": "msg_123"}

class ReniecSDK:
    def consultar(self, dni: str) -> tuple:
        if len(dni) == 8:
            return (200, {"valido": True, "nombres": "Juan Perez"})
        return (404, {"valido": False})