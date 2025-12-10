/* eslint-disable camelcase */
import { createContext, useEffect, useState, useContext } from 'react'
import { setCookie, parseCookies, destroyCookie } from 'nookies'
import Router from 'next/router'
import { signInRequest, csrfToOauth, backendLogout } from '../services/auth'
import { api } from '../services/api'
import { recoverUserInformation } from '../services/user'
import { sanitizeRedirectUrl } from '../utils/redirect'
import PropTypes from 'prop-types'

export const AuthContext = createContext({})

// Baseado neste exemplo: https://www.mikealche.com/software-development/how-to-implement-authentication-in-next-js-without-third-party-libraries
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const isAuthenticated = !!user

  useEffect(() => {
    const { 'pzserver.access_token': access_token } = parseCookies()

    if (access_token) {
      recoverUserInformation()
        .then(user => {
          setUser(user)
        })
        .catch(error => {
          console.error('AuthContext: Failed to recover user data:', error)
        })
    } else {
      const { 'pzserver.csrftoken': csrftoken } = parseCookies()
      if (csrftoken) {
        // Check if there's a returnUrl stored in sessionStorage (from SAML2 login redirect)
        let returnUrl = '/'
        if (typeof window !== 'undefined') {
          const storedReturnUrl = sessionStorage.getItem('saml_return_url')
          if (storedReturnUrl) {
            returnUrl = storedReturnUrl
            sessionStorage.removeItem('saml_return_url')
          }
        }
        
        csrfToOauth(returnUrl)
          .then(res => {
            // Load user data after login to avoid blank username on first render
            recoverUserInformation().then(loggedUser => {
              setUser(loggedUser)
              const sanitizedReturnUrl = sanitizeRedirectUrl(returnUrl, '/')
              console.log('SAML2 login successful, redirecting to:', sanitizedReturnUrl)
              setTimeout(() => {
                Router.push(sanitizedReturnUrl)
              }, 100)
            })
          })
          .catch(res => {
            console.log('AuthContext: CSRF to OAuth conversion failed')
          })
      }
    }
  }, [])

  async function signIn({ username, password, returnUrl = '/' }) {
    try {
      const { access_token, refresh_token, expires_in } = await signInRequest({
        username,
        password
      })
      
      setCookie(undefined, 'pzserver.access_token', access_token, {
        maxAge: expires_in
      })

      setCookie(undefined, 'pzserver.refresh_token', refresh_token, {
        maxAge: 30 * 24 * 60 * 60 // 30 days
      })

      // Update API instance with new token
      api.defaults.headers.Authorization = `Bearer ${access_token}`

      // Load user data after login to avoid blank username on first render
      const loggedUser = await recoverUserInformation()
      setUser(loggedUser)

      // Wait for React to process state before redirecting
      const sanitizedReturnUrl = sanitizeRedirectUrl(returnUrl, '/')
      console.log('Login successful, redirecting to:', sanitizedReturnUrl)
      setTimeout(() => {
        Router.push(sanitizedReturnUrl)
      }, 100)
    } catch (error) {
      console.error('Login process failed:', error)
      throw error
    }
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
