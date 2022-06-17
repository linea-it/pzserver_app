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
  buttonsContainer: {
    display: 'flex',
    gap: 16,
    justifyContent: 'center',
    flexWrap: 'wrap'
  }
}))

export default useStyles
