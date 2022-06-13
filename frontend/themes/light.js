import { createTheme } from '@mui/material/styles'

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
    },
    text: {
      primary: 'rgba(18,48,78,0.87)',
      secondary: 'rgba(18,48,78,0.6)',
      disabled: 'rgba(18,48,78,0.38)'
    }
    // text: {
    //   primary: 'rgb(52, 71, 103)',
    //   secondary: 'rgb(52, 71, 103, 0.6)',
    //   disabled: 'rgb(52, 71, 103, 0.38)'
    // }
  }
})

export default light
