// const delay = (amount = 750) =>
//   new Promise(resolve => setTimeout(resolve, amount))

// export async function signInRequest(data) {
//   // await delay()
//   console.log("SignInRequest")
//   // return {
//   //   token: 12345789,
//   //   user: {
//   //     name: 'Matheus Freitas',
//   //     email: 'matheus.freitas@linea.gov.br'
//   //   }
//   // }
// }

// export async function recoverUserInformation() {
//   await delay()

//   return {
//     user: {
//       name: 'Matheus Freitas',
//       email: 'matheus.freitas@linea.gov.br'
//     }
//   }
// }


import axios from 'axios'

const api = axios.create({
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json'
  }
});

export default api

export function signInRequest(data) {
  return api.post('/auth/token', {
    grant_type: 'password',
    username: data.username,
    password: data.password,
    client_id: 'jjch4SMVNaej93kZiz3oUscS6hlkh4JLR1e3diiG',
    client_secret: 'h6apxQ9d76V7CJDHMIla5pf4BQtWcUx9U0kOExj9w29SP3474EoeyAV0mBVWeHiFQFmCycUvMj0CBzIG4xbSQV7eSD9JmJvBm0F2rFEB8AICztm8dIo8ZaL3hpwfBA5s'
  }).then(res => res.data)
}
