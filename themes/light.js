import { createTheme } from '@material-ui/core/styles'

const light = createTheme({
  palette: {
    primary: {
      light: '#4f5964',
      main: '#283663',
      dark: '#24292e'
      // dark: '#283663',
      // main: '#24292e'
    },
    secondary: {
      main: '#ffdd00'
    },
    success: {
      main: '#4caf50'
    },
    error: {
      main: '#ca2c0c'
    },
    background: {
      default: '#f8f6f5'
    }
  }
})

export default light
