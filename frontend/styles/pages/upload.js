import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({

  container: {
    // height: '100vh'
  },
  gridContainer: {
    margin: `${theme.spacing(2)} 0`
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: 20
  },
  buttonsContainer: {
    display: 'flex',
    gap: 16,
    justifyContent: 'center',
    flexWrap: 'wrap'
  }
}))

export default useStyles
