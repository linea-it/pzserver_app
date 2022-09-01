/* eslint-disable camelcase */
import { createContext, useEffect, useState, useContext } from 'react'
import { setCookie, parseCookies, destroyCookie } from 'nookies'
import Router from 'next/router'
import { signInRequest, csrfToOauth, backendLogout } from '../services/auth'
import { api } from '../services/api'
import { recoverUserInformation } from '../services/user'
import PropTypes from 'prop-types'

export const AuthContext = createContext({})

// Baseado neste exemplo: https://www.mikealche.com/software-development/how-to-implement-authentication-in-next-js-without-third-party-libraries
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const isAuthenticated = !!user

  useEffect(() => {
    const { 'pzserver.access_token': access_token } = parseCookies()

    if (access_token) {
      recoverUserInformation().then(user => setUser(user))
    } else {
      // console.log('Não tem access token')
      const { 'pzserver.csrftoken': csrftoken } = parseCookies()
      if (csrftoken) {
        // console.log('Pode estar logado no Django')
        csrfToOauth()
          .then(res => {
            // Carrega os dados do usuario logo apos o login
            // Evita que no primeiro render do index o nome de usuario esteja em branco
            recoverUserInformation().then(loggedUser => {
              setUser(loggedUser)
              Router.push('/')
            })
          })
          .catch(res => {
            console.log(res)
          })
      }
    }
  }, [])

  async function signIn({ username, password }) {
    const { access_token, refresh_token, expires_in } = await signInRequest({
      username,
      password
    })
    setCookie('undefined', 'pzserver.access_token', access_token, {
      maxAge: expires_in
    })

    setCookie('undefined', 'pzserver.refresh_token', refresh_token, {
      maxAge: 30 * 24 * 60 * 60 // 30 days
    })

    // Atualiza a instancia Api com o novo token
    api.defaults.headers.Authorization = `Bearer ${access_token}`

    // Carrega os dados do usuario logo apos o login
    // Evita que no primeiro render do index o nome de usuario esteja em branco
    const loggedUser = await recoverUserInformation()
    setUser(loggedUser)

    Router.push('/')
  }

  function logout() {
    const { 'pzserver.csrftoken': csrftoken } = parseCookies()
    if (csrftoken) {
      backendLogout()
        .then(res => {
          console.log('Backend Logout Success')
        })
        .catch(res => {
          console.log('Failed on Backend logout.')
        })
    }

    destroyCookie(null, 'pzserver.access_token')
    destroyCookie(null, 'pzserver.refresh_token')
    destroyCookie(null, 'pzserver.csrftoken')
    setUser(null)

    delete api.defaults.headers.Authorization
    delete api.defaults.headers['X-CSRFToken']
    Router.push('/login')
  }

  return (
    <AuthContext.Provider
      value={{ user: user, isAuthenticated, signIn, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

AuthProvider.propTypes = {
  children: PropTypes.node
}

export const useAuth = () => useContext(AuthContext)
