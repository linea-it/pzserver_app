import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import Head from 'next/head'
import { useRouter } from 'next/router'
import PropTypes from 'prop-types'
import { useEffect, useState } from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import Footer from '../components/Footer'
import { AuthProvider } from '../contexts/AuthContext'
import '../styles/global.css'
import Header from '../components/Header'

const queryClient = new QueryClient()

export default function MyApp(props) {
  const { Component, pageProps } = props
  const route = useRouter()
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    const jssStyles = document.querySelector('#jss-server-side')
    if (jssStyles) {
      jssStyles.parentElement.removeChild(jssStyles)
    }

    const savedDarkMode = localStorage.getItem('darkMode')
    setDarkMode(savedDarkMode === 'true')
  }, [])

  const handleToggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)
    localStorage.setItem('darkMode', String(newDarkMode))
  }

  const light = createTheme({
    palette: {
      mode: 'light',
    },
  })

  const dark = createTheme({
    palette: {
      mode: 'dark',
    },
  })

  return (
    <>
      <Head>
        <title>Photo-z Server</title>
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width"
        />
      </Head>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={darkMode ? dark : light}>
          <CssBaseline />
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '100%'
            }}
          >
            <AuthProvider>
              {route.pathname !== '/login' && (
                <Header
                  darkMode={darkMode}
                  setDarkMode={handleToggleDarkMode}
                  route={route}
                />
              )}
              <Component {...pageProps} />
              {route.pathname !== '/login' && <Footer />}
            </AuthProvider>
          </div>
        </ThemeProvider>
      </QueryClientProvider>
    </>
  )
}

MyApp.propTypes = {
  Component: PropTypes.elementType.isRequired,
  pageProps: PropTypes.object.isRequired
}
