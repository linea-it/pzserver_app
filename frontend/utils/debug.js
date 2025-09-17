// Configurações de debug para o sistema de autenticação
export const DEBUG_CONFIG = {
  AUTH_FLOW: true, // Logs do fluxo de autenticação
  API_CALLS: false, // Logs das chamadas de API
  COOKIES: true, // Logs relacionados a cookies
  REDIRECTS: true, // Logs de redirecionamentos
}

export const debugLog = (category, message, data = null) => {
  if (DEBUG_CONFIG[category]) {
    const timestamp = new Date().toISOString()
    console.log(`[${timestamp}] [${category}] ${message}`, data || '')
  }
}

export const debugError = (category, message, error = null) => {
  if (DEBUG_CONFIG[category]) {
    const timestamp = new Date().toISOString()
    console.error(`[${timestamp}] [${category}] ERROR: ${message}`, error || '')
  }
}