import axios from 'axios'
import { parseCookies } from 'nookies'

const apiAuth = axios.create({
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json'
  }
});

export default apiAuth

export function signInRequest(data) {
  return apiAuth.post('/auth/token', {
    grant_type: 'password',
    username: data.username,
    password: data.password,
    client_id: 'GrMwZm6hhw81dZUG62Mmyw5bhW8I9JolE3grgPPh',
    client_secret: 'fMMu1u8GWm9zyzMPoTPTf3TaZtLAHTfu9HIi23u5Ly3mdtFtnNJgZI5FCkjfZuuKziCthNcfJ6rP50qfjkJcbzgCIIVark29EDoqPapQpHc5yUVz7hzvMtLdyA3KZ0yX'
  }).then(res => res.data)
}
