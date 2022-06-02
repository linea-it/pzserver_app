import axios from 'axios'
import { parseCookies } from 'nookies'

export function getAPIClient(ctx) {
  console.log('CTX: ', ctx)
  const { 'access_token': token } = parseCookies(ctx)

  const api = axios.create({
    // baseURL: '/api',
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      accept: 'application/json'
    }
  })

  console.log('TOKEN:', token)

  if (token) {
    api.defaults.headers.Authorization = `Bearer ${token}`
  }

  // api.interceptors.response.use(
  //   (response) => {
  //     console.log('response: ', response);
  //     return response;
  //   },
  //   async function (error) {
  //     console.log('error: ', error);
  //     if ((error.response.status === 401 || error.response.status === 403) && token) {
  //       const response = await refreshToken(error);
  //       return error;
  //     }
  //     return Promise.reject(error);
  //   }
  // );

  return api
}

async function refreshToken(error) {
  return new Promise((resolve, reject) => {
    try {
      console.log('STEP01: ', error)
      const { 'refresh_token': refresh_token } = parseCookies()
      const header = { "Content-Type": "application/json" };
      const parameters = {
        method: "POST",
        headers: header,
      };
      const body = {
        grant_type: "refresh_token",
        client_id: 'GrMwZm6hhw81dZUG62Mmyw5bhW8I9JolE3grgPPh',
        client_secret: 'fMMu1u8GWm9zyzMPoTPTf3TaZtLAHTfu9HIi23u5Ly3mdtFtnNJgZI5FCkjfZuuKziCthNcfJ6rP50qfjkJcbzgCIIVark29EDoqPapQpHc5yUVz7hzvMtLdyA3KZ0yX',
        refresh_token: refresh_token,
      };
      api
        .post(
          "/auth/token",
          body,
          parameters
        )
        .then(async (res) => {
          console.log("refreshToken", res.data);
          setCookie('undefined', 'refresh_token', res.data.refresh_token, {
            maxAge: 2000
          })
      
          setCookie('undefined', 'access_token', res.data.access_token, {
            maxAge: 2000
          })
      
          api.defaults.headers.Authorization = `Bearer ${res.data.access_token}`
        
          return resolve(res);
        })
        .catch((err) => {
          console.log('Refresh ERROR: ', err);
          window.location('/login')
        });
    } catch (err) {
      console.log('Refresh ERROR 2: ', err);
      window.location('/login')
    }
  });
};

export const api = getAPIClient()

export function recoverUserInformation() {
  return api.get('/api/logged_user').then(res => res.data)
}