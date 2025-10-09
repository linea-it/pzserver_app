/* eslint-disable camelcase */
import axios from 'axios'
import { parseCookies, setCookie } from 'nookies'
import { refreshToken } from './auth'

// REFRESH TOKEN
// DAR UMA OLHADA NESTE PACOTE: https://github.com/Flyrell/axios-auth-refresh
// Outro Exemplo de Refresh Token Usando Hook: https://dev.to/arianhamdi/react-hooks-in-axios-interceptors-3e1h

export function whichEnvironment() {

  let api = axios.create({
    timeout: 30000,
    maxContentLength: 230 * 1024 * 1024, // 230MB limit
    maxBodyLength: 230 * 1024 * 1024,    // 230MB limit
    headers: {
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })

  return api.get('/which_environment/').then((res) => {
    const result = res.data
    return result
  })
}

export function getAPIClient(ctx) {
  const api = axios.create({
    timeout: 30000,
    maxContentLength: 230 * 1024 * 1024, // 230MB limit
    maxBodyLength: 230 * 1024 * 1024,    // 230MB limit
    headers: {
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })

  // Add a request interceptor
  api.interceptors.request.use(
    function (config) {
      // Do something before request is sent
      if (!config.headers.Authorization) {
        // Adiciona o Header Authorization
        const { 'pzserver.access_token': token } = parseCookies(ctx)
        config.headers.Authorization = `Bearer ${token}`
        api.defaults.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    function (error) {
      // Do something with request error
      return Promise.reject(error)
    }
  )

  // Add a response interceptor
  api.interceptors.response.use(
    function (response) {
      // Any status code that lie within the range of 2xx cause this function to trigger
      // Do something with response data
      return response
    },
    async function (error) {
      const originalConfig = error.config
      if (error.response) {
        if (error.response.status === 401 && !originalConfig._retry) {
          // Adiciona uma flag para impedir que fique em loop
          originalConfig._retry = true

          const { 'pzserver.refresh_token': refresh_token } = parseCookies(ctx)
          const response = await refreshToken(refresh_token)

          setCookie(
            undefined,
            'pzserver.access_token',
            response.access_token,
            {
              maxAge: response.expires_in
            }
          )

          setCookie(
            undefined,
            'pzserver.refresh_token',
            response.refresh_token,
            {
              maxAge: 30 * 24 * 60 * 60 // 30 days
            }
          )

          // Atualiza a instancia Api com o novo token
          api.defaults.headers.Authorization = `Bearer ${response.access_token}`

          // Atualiza a requisiçao que falhou com o novo token para tentar novamente
          originalConfig.headers.Authorization = `Bearer ${response.access_token}`
          console.log(originalConfig)
          // return a request
          return api(originalConfig)
        }
        // if (error.response.status === ANOTHER_STATUS_CODE) {
        //   // Do something
        //   return Promise.reject(error.response.data)
        // }
      }
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        error.message = 'The connection has timed out.'
      }
      return Promise.reject(error)
    }
  )

  return api
}

export const api = getAPIClient()
