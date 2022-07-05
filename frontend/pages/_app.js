import { useEffect } from 'react'
import PropTypes from 'prop-types'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { ThemeProvider } from '@mui/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { AuthProvider } from '../contexts/AuthContext'
import light from '../themes/light'
import Header from '../components/Header'
import Footer from '../components/Footer'
import '../styles/global.css'

export default function MyApp(props) {
  const { Component, pageProps } = props
  const route = useRouter()

  useEffect(() => {
    // Remove the server-side injected CSS.
    const jssStyles = document.querySelector('#jss-server-side')
    if (jssStyles) {
      jssStyles.parentElement.removeChild(jssStyles)
    }
  }, [])

  return (
    <>
      <Head>
        <title>Photo-z Server</title>
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width"
        />
      </Head>
      <ThemeProvider theme={light}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline />
        {/* Overwriting some global CSS. */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '100%'
          }}
        >
          <AuthProvider>
            {route.pathname !== '/login' && <Header />}
            <Component {...pageProps} />
            {route.pathname !== '/login' && <Footer />}
          </AuthProvider>
        </div>
      </ThemeProvider>
    </>
  )
}

MyApp.propTypes = {
  Component: PropTypes.elementType.isRequired,
  pageProps: PropTypes.object.isRequired
}
