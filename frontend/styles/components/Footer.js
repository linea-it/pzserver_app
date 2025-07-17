import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
    float: 'right',
    height: 85,
    position: 'relative',
    zIndex: 2,
    backgroundColor: theme.palette.grey[900],
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    [theme.breakpoints.down('sm')]: {
      height: '100%'
    }
  },
  toolbar: {
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  logoLink: {
    lineHeight: 0,
    display: 'inline-block',
    verticalAlign: 'middle'
  },
  logoFooter: {
    cursor: 'pointer',
    marginLeft: '10px',
    marginRight: 0,
  },
  poweredBy: {
    display: 'inline-block',
    verticalAlign: 'middle',
    color: '#fff',
    marginRight: 16,
    marginLeft: 50,
    fontFamily: 'Roboto Condensed'
  },
  marginItem: {
    marginLeft: 20,
    marginRight: 20,
    // marginTop: 8,
    display: 'flex',
    alignItems: 'center',
    gap: 16,
    [theme.breakpoints.down('sm')]: {
      width: '100%',
      flexDirection: 'column'
    }
  },
  rsp: {
    color: '#fff',
    fontFamily: 'League Gothic',
    fontSize: 32
  },
  images_credits: {
    color: '#fff',
    paddingTop: '15px'
  },
  idacLogo: {
    marginBottom: '6px'
  }
}))

export default useStyles
