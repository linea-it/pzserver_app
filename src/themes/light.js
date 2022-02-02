import { createTheme } from '@mui/material/styles'

const light = createTheme({
  palette: {
    primary: {
      main: '#283663'
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
