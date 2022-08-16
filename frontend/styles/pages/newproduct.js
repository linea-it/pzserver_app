import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  container: {
    flex: 1,
    padding: theme.spacing(4)
  },
  gridContainer: {
    margin: `${theme.spacing(2)} 0`
  },
  formContainer: {
    // display: 'flex',
    // flexDirection: 'column',
    // gap: 20
  },
  pageHeader: {
    marginBottom: theme.spacing(5)
  },
  formBox: {
    // backgroundColor: 'red',
    height: `calc(100% - ${theme.spacing(8)})`
  },
  formPaper: {
    height: '100%'
    // backgroundColor: 'black'
  },
  formGrid: {
    height: '100%'
  },
  leftPanel: {
    height: '100%',
    backgroundImage: 'url(/upload.jpg)'
  },
  rightPanel: {
    height: '100%'
  },
  stepLabel: {
    color: 'white'
  },
  stepper: {
    paddingBottom: theme.spacing(2)
  },
  stepDescription: {
    paddingBottom: theme.spacing(2)
  }
}))

export default useStyles
