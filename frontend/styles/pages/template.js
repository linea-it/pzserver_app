import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  root: {
    transition: 'box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms',
    borderRadius: '4px',
    padding: theme.spacing(3),
    flex: '1 1 0%',
    background: 'rgb(247, 249, 252)'
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
    marginTop: theme.spacing(2),
    marginBotton: theme.spacing(2)
  },
  gridContent: {
    display: 'flex',
    flexFlow: 'row wrap',
    margin: theme.spacing(2)
  }
}))

export default useStyles
