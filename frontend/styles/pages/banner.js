import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
    banner: {
        position: 'relative',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: `url('/interfaces/banner_lsst_summit.jpg')`,
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
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
}))

export default useStyles
