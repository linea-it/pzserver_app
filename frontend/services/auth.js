import axios from 'axios'

const apiAuth = axios.create({
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json'
  }
})

export default apiAuth

export function signInRequest(data) {
  return apiAuth
    .post('/auth/token', {
      grant_type: 'password',
      username: data.username,
      password: data.password,
      client_id: 'lKPub4YnYGeUq77VIys0gGPoDh25NB0oKv4vwH5G',
      client_secret:
        'yQPmjBJwx9DsZ1QkTQaTqRbC9QQ3MMUgVex7NRvFh7PVXG9kEjE9EOkvprFnctfBtzsF4cC8aJp8vhfpQr75HxZ8kbUJzS7m7ZG8tbFmxqyXJTIajXiWjbvYiaWfguHs'
    })
    .then(res => res.data)
}
