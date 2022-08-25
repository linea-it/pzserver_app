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

export async function csrfToOauth() {
  const response = await fetch('/front-api/config')
  const oauthSecret = await response.json()

  const ax = axios.create({
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })
  ax.defaults.xsrfCookieName = 'csrftoken'
  ax.defaults.xsrfHeaderName = 'X-CSRFToken'
  ax.defaults.withCredentials = true

  return ax
    .post('/api/csrf_oauth/', {
      client_id: oauthSecret.client_id
    })
    .then(res => res.data)
}
