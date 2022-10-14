import { api } from './api'

export async function recoverUserInformation() {
  const res = await api.post('/api/logged_user/')
  return res.data
}

export async function generateApiToken() {
  return api.post('/api/get_token/')
}
