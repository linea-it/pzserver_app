import { createContext, useEffect, useState } from 'react'
import { setCookie, parseCookies } from 'nookies'
import Router from 'next/router'
import { recoverUserInformation, signInRequest } from '../services/auth'
import { api } from '../services/api'

export const AuthContext = createContext({})

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const isAuthenticated = !!user

  useEffect(() => {
    const { 'pzserver.token': token } = parseCookies()

    if (token) {
      recoverUserInformation().then(res => setUser(res.user))
    }
  }, [])

  async function signIn({ username, password }) {
    const { token, user } = await signInRequest({
      username,
      password
    })

    setCookie(undefined, 'pzserver.token', token, {
      maxAge: 60 * 60 * 24 * 2 // 2 days
    })

    api.defaults.headers.Authorization = `Bearer ${token}`

    setUser(user)

    Router.push('/')
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, signIn }}>
      {children}
    </AuthContext.Provider>
  )
}
