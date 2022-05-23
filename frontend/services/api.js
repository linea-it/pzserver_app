import axios from 'axios'

export function getAPIClient(ctx) {
  // const { 'pzserver.token': token } = parseCookies(ctx)

  const api = axios.create({
    baseURL: '/api',
    timeout: 5000,
    headers: {
      // Authorization: 'Bearer ' + localStorage.getItem('access_token'),
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })

  if (typeof window !== 'undefined') {
    api.defaults.headers.Authorization = `Bearer ${localStorage.getItem(
      'access_token'
    )}`
  }

  return api
}

export const api = getAPIClient()

export function recoverUserInformation() {
  return api.get('/logged_user').then(res => res.data)
}
