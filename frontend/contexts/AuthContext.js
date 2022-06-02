import { createContext, useEffect, useState } from 'react'
import { setCookie, parseCookies } from 'nookies'
import Router from 'next/router'
import { apiAuth, signInRequest } from '../services/auth'
import { recoverUserInformation } from '../services/api'

export const AuthContext = createContext({})

export function AuthProvider({ children }) {
  const [userInfo, setUserInfo] = useState(null)

  const isAuthenticated = !!userInfo

  useEffect(() => {
    const { access_token } = parseCookies()

    if (access_token && !userInfo) {
      console.log('Sem informação usuario')
      recoverUserInformation().then(res => setUserInfo(res.user))
    }
  }, [])

  async function signIn({ username, password }) {
    const { access_token, refresh_token } = await signInRequest({
      username,
      password
    })

    setCookie('undefined', 'refresh_token', refresh_token, {
      maxAge: 2000,
    })

    setCookie('undefined', 'access_token', access_token, {
      maxAge: 2000
    })

    // apiAuth.defaults.headers.Authorization = `Bearer ${access_token}`

    Router.push('/')
  }

  return (
    <AuthContext.Provider value={{ user: userInfo, isAuthenticated, signIn }}>
      {children}
    </AuthContext.Provider>
  )
}
