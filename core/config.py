# core/config.py
# ===============
# Central configuration: loads roles.yaml and .env API keys.
# core/config.py
# Configurația modelului ales de echipă după testele din Cursul 2.
# Nu puneți chei API aici. Cheile rămân doar în fișierul local .env.

PROVIDER_PRINCIPAL = "gemini"
MODEL_PRINCIPAL = "gemini-2.5-flash-lite"
PROVIDER_FALLBACK = "deepseek"
MODEL_FALLBACK = "deepseek-chat"
#PROVIDER_FALLBACK = "openrouter"
#MODEL_FALLBACK = "openrouter/free"

TEMPERATURE = 0