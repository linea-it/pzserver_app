import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
  list: {
    padding: 0
  },
  avatar: {
    marginRight: 10
  },
  appbar: {
    background: theme.palette.grey[900]
  },
  separator: {
    flexGrow: 1
  },
  menuList: {
    display: 'flex',
    [theme.breakpoints.down('xs')]: {
      flexDirection: 'column'
    }
  },
  menuListItem: {
    [theme.breakpoints.down('xs')]: {
      justifyContent: 'center',
      padding: `${theme.spacing(1)}px 0`
    }
  },
  menuLink: {
    color: '#fff',
    textDecoration: 'none',
    fontWeight: 500,
    textTransform: 'uppercase',
    whiteSpace: 'nowrap'
  },
  // logoLIneA: {
  //   maxWidth: 64
  // },
  toolbar: {
    display: 'flex',
    [theme.breakpoints.down('xs')]: {
      flexDirection: 'column'
    }
  },
  banner: {
    position: 'relative',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'url(/header.jpg)',
    backgroundRepeat: 'no-repeat',
    backgroundSize: 'cover',
    // backgroundPositionY: '-400px'
    // height: '30%'
    // marginBottom: theme.spacing(4)
  },
  container: {
    background: 'transparent',
    position: 'relative',
    textAlign: 'center',
    color: '#FFF',
    zIndex: 2,
    marginTop: '0'
  },
  titleWrapper: {
    [theme.breakpoints.up('sm')]: {
      justifyContent: 'center',
      alignItems: 'center'
    },
    [theme.breakpoints.down('xl')]: {
      minHeight: 180
    },
    [theme.breakpoints.only('xl')]: {
      minHeight: 280
    }
  },
  title: {
    fontFamily: 'Oxanium',
    fontWeight: 100,
    fontSize: 50,
    [theme.breakpoints.down('sm')]: {
      fontSize: 48,
      margin: `${theme.spacing(5)}px ${theme.spacing(2)}px`
    },
    [theme.breakpoints.down('xl')]: {
      margin: `${theme.spacing(4)}`
    },
    [theme.breakpoints.only('xl')]: {
      margin: `${theme.spacing(6)}`
    },
    textShadow: 'black 0.1em 0.1em 0.2em'
  },
  socialWrapper: {
    color: '#fff',
    position: 'absolute',
    right: 0,
    bottom: 0,
    zIndex: 2
  },
  social: {
    margin: '0 12px'
  }
}))

export default useStyles
