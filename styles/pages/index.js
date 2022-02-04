import { makeStyles } from '@material-ui/core/styles'

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
    height: 'calc(100% - 128px)',
    flexDirection: 'column'
  },
  banner: {
    position: 'relative',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'url(/header.jpg)',
    backgroundRepeat: 'no-repeat',
    backgroundSize: 'cover',
    height: '50%'
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
  title: {
    fontFamily: 'Oxanium',
    fontWeight: 100,
    fontSize: 50,
    margin: 0,
    [theme.breakpoints.down('sm')]: {
      fontSize: 48,
      margin: `0 ${theme.spacing(2)}px`
    },
    textShadow: 'black 0.1em 0.1em 0.2em'
  },
  titleWrapper: {
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    }
  },
  socialWrapper: {
    color: '#fff',
    position: 'absolute',
    right: 0,
    bottom: 0,
    zIndex: 2
  },
  interfaceContainer: {
    gap: 16,

    [theme.breakpoints.down('sm')]: {
      margin: 16
    }
  },

  main: {
    position: 'relative',
    zIndex: 2,
    height: '100%',
    display: 'flex',
    alignItems: 'center'
  },
  titleItem: {
    fontFamily: 'Oxanium',
    fontSize: '1.5em',
    paddingTop: '0.5em',
    paddingLeft: '1em',
    color: 'white',
    textShadow: '0.1em 0.1em 0.1em black'
  },
  media: {
    minHeight: 220
  },

  gridApplicationLg: {
    [theme.breakpoints.up('lg')]: {
      width: '20%',
      maxWidth: '20%'
    }
  }
}))

export default useStyles
