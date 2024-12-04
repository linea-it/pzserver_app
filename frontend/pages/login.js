import GitHubIcon from '@mui/icons-material/GitHub'
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
import { styled } from '@mui/material/styles'
import Image from 'next/image'
import PropTypes from 'prop-types'
import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

const GitHubButton = styled(Button)(({ theme }) => ({
  color: theme.palette.getContrastText('#000'),
  backgroundColor: '#000',
  '&:hover': {
    backgroundColor: '#333'
  }
}))

function Login({ shibLoginUrl, CILogonUrl, GithubUrl }) {
  const [isLocalhost, setIsLocalhost] = useState(false)
  const { signIn } = useAuth()
  const [formError, setFormError] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    setIsLocalhost(window.location.hostname === 'localhost')
  }, [])

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
      await signIn({ username, password })
    } catch (error) {
      setFormError('Authentication failed. Please try again.')
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
            src="https://identity.linea.org.br/eds/images/linea-logo.png"
            alt="LIneA Logo"
            width={120}
            height={100}
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
            {isLocalhost ? (
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
                        src="https://identity.linea.org.br/eds/images/cilogon_logo.png"
                        alt="CILogon Logo"
                        width={20}
                        height={20}
                      />
                    }
                    href={CILogonUrl || shibLoginUrl}
                    sx={{
                      backgroundColor: '#283663',
                      color: '#fff',
                      '&:hover': {
                        backgroundColor: '#3b4a8c'
                      }
                    }}
                  >
                    LOGIN WITH CILOGON (RSP ACCOUNT)
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <GitHubButton
                    fullWidth
                    variant="contained"
                    startIcon={<GitHubIcon />}
                    href={GithubUrl || shibLoginUrl}
                  >
                    Login with GitHub
                  </GitHubButton>
                </Grid>
              </>
            )}
          </Grid>
          <Typography textAlign="center" color="#283661" mt={2}>
            New user? Register here:{' '}
            <a
              href="https://docs.google.com/forms/d/e/1FAIpQLSdpPhOpFnb4zS-DwMEgYG-n6RWoBWpxKfRvzUnIr_v5ZSYmaA/viewform"
              target="_blank"
              rel="noopener noreferrer"
            >
              English
            </a>{' '}
            or{' '}
            <a
              href="https://docs.google.com/forms/d/e/1FAIpQLScQuUTV7Wc-C10gWNcznorbW5mOQlGkFAXUikd0R7JzsdgSfQ/viewform"
              target="_blank"
              rel="noopener noreferrer"
            >
              Português
            </a>
          </Typography>
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

Login.propTypes = {
  shibLoginUrl: PropTypes.string,
  CILogonUrl: PropTypes.string,
  GithubUrl: PropTypes.string
}

Login.defaultProps = {
  shibLoginUrl: null,
  CILogonUrl: null,
  GithubUrl: null
}

export default Login
