import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  root: {
    flex: 1,
    padding: theme.spacing(4)
  },
  pageHeader: {
    marginBottom: theme.spacing(5)
  },
  paper: {
    padding: theme.spacing(3)
  }
}))

export default useStyles
