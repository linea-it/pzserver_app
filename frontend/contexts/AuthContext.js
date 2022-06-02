/* eslint-disable camelcase */
import { createContext, useEffect, useState, useContext } from 'react'
import { setCookie, parseCookies, destroyCookie } from 'nookies'
import Router from 'next/router'
import { signInRequest } from '../services/auth'
import { api } from '../services/api'
import { recoverUserInformation } from '../services/user'
import PropTypes from 'prop-types'

export const AuthContext = createContext({})

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const isAuthenticated = !!user

  useEffect(() => {
    const { 'pzserver.access_token': access_token } = parseCookies()

    if (access_token) {
      recoverUserInformation().then(user => setUser(user))
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
    destroyCookie(null, 'pzserver.access_token')
    destroyCookie(null, 'pzserver.refresh_token')
    setUser(null)
    delete api.defaults.headers.Authorization
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
