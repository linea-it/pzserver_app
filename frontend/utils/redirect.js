/**
 * Utilidades para validar e sanitizar URLs de redirecionamento
 */

/**
 * Valida se uma URL é segura para redirecionamento
 * @param {string} url - URL para validar
 * @returns {boolean} - true se a URL é segura
 */
export function isValidRedirectUrl(url) {
  if (!url || typeof url !== 'string') {
    return false
  }

  try {
    // URLs relativas são sempre válidas
    if (url.startsWith('/')) {
      // Evita double slashes que podem ser interpretados como URLs absolutas
      if (url.startsWith('//')) {
        return false
      }
      return true
    }

    // Para URLs absolutas, verificar se são do mesmo domínio
    const urlObj = new URL(url)
    const currentHost =
      typeof window !== 'undefined' ? window.location.host : 'localhost'

    return urlObj.host === currentHost
  } catch (error) {
    // URL malformada
    return false
  }
}

/**
 * Sanitiza uma URL de redirecionamento
 * @param {string} url - URL para sanitizar
 * @param {string} fallback - URL de fallback (padrão: '/')
 * @returns {string} - URL sanitizada
 */
export function sanitizeRedirectUrl(url, fallback = '/') {
  if (!url) {
    return fallback
  }

  const decodedUrl = decodeURIComponent(url)

  if (isValidRedirectUrl(decodedUrl)) {
    return decodedUrl
  }

  console.warn(
    'URL de redirecionamento inválida:',
    url,
    'usando fallback:',
    fallback
  )
  return fallback
}

/**
 * Constrói uma URL de login com returnUrl
 * @param {string} returnUrl - URL para retornar após login
 * @returns {string} - URL do login com parâmetro de retorno
 */
export function buildLoginUrl(returnUrl) {
  if (!returnUrl || returnUrl === '/') {
    return '/login'
  }

  const encodedReturnUrl = encodeURIComponent(returnUrl)
  return `/login?returnUrl=${encodedReturnUrl}`
}

/**
 * Constrói uma URL de login SAML com o parâmetro next dinâmico.
 * @param {string} loginUrl - URL base de login SAML/SATOSA
 * @param {string} returnUrl - URL para retornar após autenticação
 * @returns {string|null} - URL final de login SAML
 */
export function buildSamlLoginUrl(loginUrl, returnUrl = '/') {
  if (!loginUrl) {
    return null
  }

  const sanitizedReturnUrl = sanitizeRedirectUrl(returnUrl, '/')

  try {
    const baseOrigin =
      typeof window !== 'undefined'
        ? window.location.origin
        : 'http://localhost'
    const parsedUrl = new URL(loginUrl, baseOrigin)

    parsedUrl.searchParams.set('next', sanitizedReturnUrl)

    // Preserve relative URLs when the configured login URL is relative.
    if (loginUrl.startsWith('/')) {
      return `${parsedUrl.pathname}${parsedUrl.search}${parsedUrl.hash}`
    }

    return parsedUrl.toString()
  } catch (error) {
    console.warn(
      'Falha ao montar URL de login SAML, usando URL original:',
      loginUrl,
      error
    )
    return loginUrl
  }
}
