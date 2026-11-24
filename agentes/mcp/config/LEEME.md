# Ejemplos de configuración para CitaSalud MCP

Abre el repositorio como espacio de trabajo y usa el entorno `.venv` con las dependencias de `agentes/mcp/requirements.txt`. Los ejemplos con rutas relativas se resuelven desde la raíz del repositorio.

| Host | Archivo | Ubicación |
|---|---|---|
| VS Code + GitHub Copilot (modo agente) | `vscode_mcp.json` | copiar como `.vscode/mcp.json` en la raíz del repositorio |
| Claude Code | `claude_code_mcp.json` | copiar como `.mcp.json` en la raíz |
| Gemini CLI | `gemini_settings.json` | fusionar en `.gemini/settings.json` del proyecto |

Configura el host para pedir aprobación humana antes de cada llamada a `reservar_cita_borrador`. La verificación de E2 usa el cliente local `agentes/mcp/cliente/explorar.py`.
