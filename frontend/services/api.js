/* eslint-disable camelcase */
import axios from 'axios'
import { parseCookies, setCookie } from 'nookies'
import { refreshToken } from './auth'

// REFRESH TOKEN
// DAR UMA OLHADA NESTE PACOTE: https://github.com/Flyrell/axios-auth-refresh
// Outro Exemplo de Refresh Token Usando Hook: https://dev.to/arianhamdi/react-hooks-in-axios-interceptors-3e1h

export function getAPIClient(ctx) {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  const api = axios.create({
    // baseURL: '/api',
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })

  if (token) {
    api.defaults.headers.Authorization = `Bearer ${token}`
  }

  api.interceptors.response.use(
    response => {
      return response
    },
    async error => {
      const originalConfig = error.config
      if (error.response) {
        if (error.response.status === 401 && !originalConfig._retry) {
          // Adiciona uma flag para impedir que fique em loop
          originalConfig._retry = true

          // Call refreshToken() request
          console.log('Não Autorizado')
          const { 'pzserver.refresh_token': refresh_token } = parseCookies(ctx)
          const response = await refreshToken(refresh_token)
          console.log(response)

          setCookie(
            'undefined',
            'pzserver.access_token',
            response.access_token,
            {
              maxAge: response.expires_in
            }
          )

          setCookie(
            'undefined',
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
      return Promise.reject(error)
    }
  )

  return api
}

// async function refreshToken(error) {
//   return new Promise((resolve, reject) => {
//     try {
//       console.log('STEP01: ', error)
//       const { 'refresh_token': refresh_token } = parseCookies()
//       const header = { "Content-Type": "application/json" };
//       const parameters = {
//         method: "POST",
//         headers: header,
//       };
//       const body = {
//         grant_type: "refresh_token",
//         client_id: 'GrMwZm6hhw81dZUG62Mmyw5bhW8I9JolE3grgPPh',
//         client_secret: 'fMMu1u8GWm9zyzMPoTPTf3TaZtLAHTfu9HIi23u5Ly3mdtFtnNJgZI5FCkjfZuuKziCthNcfJ6rP50qfjkJcbzgCIIVark29EDoqPapQpHc5yUVz7hzvMtLdyA3KZ0yX',
//         refresh_token: refresh_token,
//       };
//       api
//         .post(
//           "/auth/token",
//           body,
//           parameters
//         )
//         .then(async (res) => {
//           console.log("refreshToken", res.data);
//           setCookie('undefined', 'refresh_token', res.data.refresh_token, {
//             maxAge: 2000
//           })

//           setCookie('undefined', 'access_token', res.data.access_token, {
//             maxAge: 2000
//           })

//           api.defaults.headers.Authorization = `Bearer ${res.data.access_token}`

//           return resolve(res);
//         })
//         .catch((err) => {
//           console.log('Refresh ERROR: ', err);
//           window.location('/login')
//         });
//     } catch (err) {
//       console.log('Refresh ERROR 2: ', err);
//       window.location('/login')
//     }
//   });
// };

export const api = getAPIClient()
