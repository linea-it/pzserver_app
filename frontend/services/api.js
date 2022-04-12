import axios from 'axios'
import { parseCookies } from 'nookies'

export function getAPIClient(ctx) {
  const { 'pzserver.token': token } = parseCookies(ctx)

  const api = axios.create({
    baseURL: '/api'
  })

  if (token) {
    api.defaults.headers.Authorization = `Bearer ${token}`
  }

  return api
}

export const api = getAPIClient()
