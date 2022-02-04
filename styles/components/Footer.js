import { makeStyles } from '@material-ui/core/styles'

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
    float: 'right',
    height: 64,
    position: 'fixed'
  },
  appBarDrawerClose: {
    top: 'auto',
    zIndex: 2,
    bottom: 0,
    backgroundColor: '#212121',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    })
  },
  toolbar: {
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  versionLink: {
    color: '#d2cf00',
    textDecoration: 'none',
    fontSize: '0.9rem',
    cursor: 'pointer',
    display: 'inline-block',
    verticalAlign: 'middle'
  },
  logoLink: {
    lineHeight: 0,
    display: 'inline-block',
    verticalAlign: 'middle'
  },
  poweredBy: {
    display: 'inline-block',
    verticalAlign: 'middle',
    color: '#fff'
  },
  logoFooter: {
    cursor: 'pointer',
    marginLeft: '10px',
    maxWidth: 52
  },
  marginItem: {
    marginLeft: 20,
    marginRight: 20,
    marginTop: 8
  }
}))

export default useStyles
