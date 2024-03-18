import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider } from '@mui/material/styles'
import Box from '@mui/material/Box'
import Head from 'next/head'
import { useRouter } from 'next/router'
import PropTypes from 'prop-types'
import { useEffect, useState } from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import Footer from '../components/Footer'
import { AuthProvider } from '../contexts/AuthContext'
import lightTheme from '../themes/light'
import darkTheme from '../themes/dark'
import '../styles/global.css'
import Header from '../components/Header'

const queryClient = new QueryClient()

export default function MyApp(props) {
  const { Component, pageProps } = props
  const route = useRouter()
  const [darkMode, setDarkMode] = useState(false)
  const [scrollNeeded, setScrollNeeded] = useState(false)

  useEffect(() => {
    const jssStyles = document.querySelector('#jss-server-side')
    if (jssStyles) {
      jssStyles.parentElement.removeChild(jssStyles)
    }

    const darkModePreference = localStorage.getItem('darkMode')
    if (darkModePreference) {
      setDarkMode(darkModePreference === '1')
    }

    handleScroll()
  }, [])

  useEffect(() => {
    handleScroll()
  }, [route.pathname])

  const handleScroll = () => {
    const contentHeight = document.body.scrollHeight
    const windowHeight = window.innerHeight
    const hasVerticalScrollbar = contentHeight > windowHeight

    setScrollNeeded(hasVerticalScrollbar)
  }

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
        <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
          <CssBaseline />
          <Box
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: '100vh',
              overflowY: scrollNeeded ? 'auto' : 'hidden'
            }}
          >
            <AuthProvider>
              {route.pathname !== '/login' && (
                <Header
                  darkMode={darkMode}
                  setDarkMode={setDarkMode}
                  route={route}
                />
              )}
              <Component {...pageProps} />
              {route.pathname !== '/login' && <Footer />}
            </AuthProvider>
          </Box>
        </ThemeProvider>
      </QueryClientProvider>
    </>
  )
}

MyApp.propTypes = {
  Component: PropTypes.elementType.isRequired,
  pageProps: PropTypes.object.isRequired
}
