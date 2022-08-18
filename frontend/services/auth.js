import axios from 'axios'

const apiAuth = axios.create({
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json'
  }
})

export default apiAuth

export async function signInRequest(data) {
  const response = await fetch('/front-api/config')
  const oauthSecret = await response.json()

  return apiAuth
    .post('/api/auth/token', {
      grant_type: 'password',
      username: data.username,
      password: data.password,
      client_id: oauthSecret.client_id,
      client_secret: oauthSecret.client_secret
    })
    .then(res => res.data)
}

export async function refreshToken(token) {
  const response = await fetch('/front-api/config')
  const oauthSecret = await response.json()
  const res = await apiAuth.post('/api/auth/token', {
    grant_type: 'refresh_token',
    client_id: oauthSecret.client_id,
    client_secret: oauthSecret.client_secret,
    refresh_token: token
  })
  return res.data
}
