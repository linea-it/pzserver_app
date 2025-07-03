import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  root: {
    transition: 'box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms',
    borderRadius: '4px',
    padding: theme.spacing(3),
    flex: '1 1 0%',
  },
  gridTitle: {
    display: 'flex',
    flexFlow: 'row wrap',
    '-webkit-box-pack': 'justify',
    justifyContent: 'space-between',
    margin: theme.spacing(2)
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.25
  },
  titleDivider: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
    marginLeft: theme.spacing(2),
    width: '100%'
  },
  gridContent: {
    display: 'flex',
    flexFlow: 'row wrap'
  }
}))

export default useStyles
