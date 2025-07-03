import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  root: {
    flex: 1,
    padding: theme.spacing(4)
  },
  codeBlock: {
    display: 'block',
    padding: theme.spacing(2),
    margin: 0,
    borderRadius: '2px',
    overflowX: 'auto',
    background: theme.palette.mode === 'light' ? theme.palette.grey[200] : theme.palette.grey[700]
  }
}))

export default useStyles
