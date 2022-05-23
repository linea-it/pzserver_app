import { createContext, useEffect, useState } from 'react'
import { setCookie, parseCookies } from 'nookies'
import Router from 'next/router'
import { signInRequest } from '../services/auth'
import { recoverUserInformation } from '../services/api'
// import { api } from '../services/auth'

export const AuthContext = createContext({})

export function AuthProvider({ children }) {
  const [userInfo, setUserInfo] = useState(null)

  const isAuthenticated = !userInfo

  useEffect(() => {

    console.log('isAuthenticated: %o', isAuthenticated)

    if (!userInfo) {
      console.log('Sem informação usuario')
      recoverUserInformation().then(res => setUserInfo(res.user))
    }
  }, [])

  async function signIn({ username, password }) {
    const { access_token, refresh_token } = await signInRequest({
      username,
      password
    })

    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)

    Router.push('/')
  }

  return (
    <AuthContext.Provider value={{ user: userInfo, isAuthenticated, signIn }}>
      {children}
    </AuthContext.Provider>
  )
}
