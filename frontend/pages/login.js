import {
  Alert,
  Box,
  Button,
  Container,
  Grid,
  Snackbar,
  TextField,
  Typography
} from '@mui/material'
import Image from 'next/image'
import { parseCookies } from 'nookies'
import PropTypes from 'prop-types'
import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { sanitizeRedirectUrl } from '../utils/redirect'

function Login({ shibLoginUrl, CILogonUrl, returnUrl }) {
  const { signIn } = useAuth()
  const [formError, setFormError] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  // Converter returnUrl relativa em URL absoluta
  const absoluteReturnUrl = (() => {
    if (!returnUrl) return '/'

    // Se já for uma URL absoluta, retorna como está
    if (returnUrl.startsWith('http://') || returnUrl.startsWith('https://')) {
      return returnUrl
    }

    // Converter URL relativa em absoluta
    if (typeof window !== 'undefined') {
      return `${window.location.origin}${
        returnUrl.startsWith('/') ? '' : '/'
      }${returnUrl}`
    }

    // No servidor, retornar a URL relativa
    return returnUrl
  })()

  const encodedReturnUrl = encodeURIComponent(absoluteReturnUrl)

  // Substituir o parâmetro 'next' na CILogonUrl com encodedReturnUrl
  const modifiedCILogonUrl = CILogonUrl
    ? (() => {
        try {
          const url = new URL(CILogonUrl)
          url.searchParams.set('next', encodedReturnUrl)
          return url.toString()
        } catch (e) {
          return CILogonUrl
        }
      })()
    : null

  console.log('Return URL:', returnUrl)
  console.log('Modified CILogon URL:', modifiedCILogonUrl)

  const handleSnackbarErrorClose = (_, reason) => {
    if (reason === 'clickaway') return
    setFormError('')
  }

  const handleSignIn = async e => {
    e.preventDefault()

    if (!username || !password) {
      setFormError('Username and Password are required')
      return
    }

    try {
      const sanitizedReturnUrl = sanitizeRedirectUrl(returnUrl, '/')
      await signIn({ username, password, returnUrl: sanitizedReturnUrl })
    } catch (error) {
      console.error('Login form error:', error)
      const errorMessage =
        error.response?.data?.error_description ||
        error.response?.data?.detail ||
        error.message ||
        'Authentication failed. Please try again.'
      setFormError(errorMessage)
    }
  }

  return (
    <Container
      component="main"
      maxWidth="md"
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh'
      }}
    >
      <Grid
        container
        sx={{
          width: '90%',
          backgroundColor: '#fff',
          borderRadius: '20px',
          padding: '32px',
          boxShadow:
            '0px 2px 1px -1px rgba(0, 0, 0, 0.2), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)'
        }}
      >
        <Grid
          item
          xs={12}
          md={6}
          sx={{
            display: 'flex',
            justifyContent: 'left',
            alignItems: 'center'
          }}
        >
          <Image
            src="/logo_idac.png"
            alt="LIneA Logo"
            width={140}
            height={130}
          />
          <Image
            src="/vc-rubin.png"
            alt="Rubin Logo"
            width={170}
            height={175}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography
            component="h3"
            variant="h5"
            textAlign="center"
            fontWeight="bold"
            color="#283661"
            mt={4}
          >
            Welcome to PZ Server
          </Typography>
          <Grid container spacing={2} mt={4}>
            {!CILogonUrl ? (
              <>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Username"
                    variant="outlined"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    variant="outlined"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    onClick={handleSignIn}
                  >
                    Sign In
                  </Button>
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={
                      <Image
                        src="/cilogon_logo.png"
                        alt="CILogon Logo"
                        width={20}
                        height={20}
                      />
                    }
                    href={modifiedCILogonUrl || shibLoginUrl}
                    sx={{
                      backgroundColor: '#283663',
                      color: '#fff',
                      bottom: 20,
                      '&:hover': {
                        backgroundColor: '#3b4a8c'
                      }
                    }}
                  >
                    LOGIN LSST MEMBERS (RSP ACCOUNT)
                  </Button>
                </Grid>
              </>
            )}
          </Grid>
        </Grid>
        <Typography
          textAlign="center"
          color="#283661"
          mt={2}
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            width: '100%'
          }}
        >
          Any problem authenticating or registering?{' '}
          <Box component="span" sx={{ mx: 0.5 }}></Box>
          <a
            href="mailto:helpdesk@linea.org.br"
            target="_blank"
            rel="noopener noreferrer"
          >
            Contact our helpdesk
          </a>
          .
        </Typography>
      </Grid>
      <Snackbar
        open={formError !== ''}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        autoHideDuration={6000}
        onClose={handleSnackbarErrorClose}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleSnackbarErrorClose}
          severity="error"
        >
          {formError}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export async function getServerSideProps(ctx) {
  const { 'pzserver.access_token': token } = parseCookies(ctx)
  // Capture returnUrl from query string
  const returnUrl = ctx.query.returnUrl || '/'

  // Validação melhorada do token
  if (token) {
    try {
      // Tenta fazer uma requisição simples para validar o token
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/logged_user/`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )
      if (response.ok) {
        // Valid token, redirect to returnUrl or home
        const sanitizedReturnUrl = sanitizeRedirectUrl(returnUrl, '/')
        return {
          redirect: {
            destination: sanitizedReturnUrl,
            permanent: false
          }
        }
      } else {
        // Invalid token, allow access to login page
        console.log('Invalid token detected on server')
      }
    } catch (error) {
      // Validation error, allow access to login page
      console.log('Token validation error:', error.message)
    }
  }

  const CILogonLoginUrl = process.env.AUTH_CILOGON_URL
    ? process.env.AUTH_CILOGON_URL
    : null

  return {
    props: {
      shibLoginUrl: null,
      CILogonUrl: CILogonLoginUrl,
      returnUrl: returnUrl
    }
  }
}

Login.propTypes = {
  shibLoginUrl: PropTypes.string,
  CILogonUrl: PropTypes.string,
  returnUrl: PropTypes.string
}

Login.defaultProps = {
  shibLoginUrl: null,
  CILogonUrl: null,
  returnUrl: null
}

export default Login
