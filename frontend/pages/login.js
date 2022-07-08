import { useRef, useState } from 'react'
import {
  Avatar,
  Button,
  TextField,
  Grid,
  Typography,
  Container,
  Snackbar
} from '@mui/material'
import Alert from '@mui/material/Alert'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import Link from '../components/Link'
import useStyles from '../styles/pages/login'
import { parseCookies } from 'nookies'
import { useAuth } from '../contexts/AuthContext'
import { grey } from '@mui/material/colors'
import { styled } from '@mui/material/styles'
import GitHubIcon from '@mui/icons-material/GitHub'

function Login(props) {
  const { shibLoginUrl, ...rest } = props

  const formRef = useRef(null)
  const classes = useStyles()
  const { signIn } = useAuth()

  const [formError, setFormError] = useState('')

  const handleSignIn = async e => {
    e.preventDefault()

    const form = formRef.current
    const username = form.username.value
    const password = form.password.value

    await signIn({ username, password })
  }

  const handleSnackbarErrorClose = (event, reason) => {
    if (reason === 'clickaway') {
      return
    }

    setFormError('')
  }

  const GitHubButton = styled(Button)(({ theme }) => ({
    color: theme.palette.getContrastText(grey[900]),
    backgroundColor: grey[900],
    '&:hover': {
      backgroundColor: grey[800]
    }
  }))

  return (
    <Container component="main" maxWidth="xs" className={classes.container}>
      <div className={classes.paper}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <form
          ref={formRef}
          className={classes.form}
          noValidate
          onSubmit={handleSignIn}
        >
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            error={formError !== ''}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            error={formError !== ''}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
          >
            Sign In
          </Button>
          {shibLoginUrl !== null && (
            <GitHubButton
              startIcon={<GitHubIcon />}
              fullWidth
              variant="contained"
              href={shibLoginUrl}
            >
              Login With GitHub
            </GitHubButton>
          )}
          <Grid container>
            <Grid item xs>
              <Link href="/" variant="body2">
                Forgot your password?
              </Link>
            </Grid>
            {/* <Grid item>
              <Link href="/" variant="body2">
                Não tem uma conta? Cadastre-se
              </Link>
            </Grid> */}
          </Grid>
        </form>
      </div>
      <Grid className={classes.copyrightContainer}>
        <Typography variant="body2" color="textSecondary" align="center">
          {'Copyright © LIneA '}
          {new Date().getFullYear()}
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

export async function getServerSideProps({ ctx }) {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (token) {
    return {
      redirect: {
        destination: '/',
        permanent: false
      }
    }
  }
  console.log(process.env)
  const shibbolethLoginUrl = process.env.AUTH_SHIB_URL
    ? process.env.AUTH_SHIB_URL
    : null

  return {
    props: {
      shibLoginUrl: shibbolethLoginUrl
    }
  }
}

export default Login
