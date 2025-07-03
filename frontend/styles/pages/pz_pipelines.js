import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
    root: {
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
    },
    pipelinesContainer: {
        gap: 16,

        [theme.breakpoints.down('sm')]: {
            margin: 16
        }
    },
    main: {
        position: 'relative',
        zIndex: 2,
        display: 'flex',
        alignItems: 'center',
        height: '100%',
        padding: '20px 0'
    },
    titleItem: {
        fontFamily: 'Oxanium',
        fontSize: '1.5em',
        paddingTop: '0.5em',
        color: 'white',
        textShadow: '0.1em 0.1em 0.1em black',
        background: 'rgba(100, 100, 100, 0.5)',
        textDecoration: 'none',
        textAlign: 'center'
    },
    ItemDescription: {
        fontFamily: 'Oxanium',
        fontSize: '1em',
        paddingLeft: '1em',
        color: 'white',
        textShadow: '0.1em 0.1em 0.1em black',
        position: 'absolute',
        bottom: '1em',
        background: 'rgba(0, 0, 0, 0.6)'
    },
    media: {
        minHeight: 260,
        [theme.breakpoints.down('xl')]: {
            minHeight: 200
        }
    },

    gridApplicationLg: {
        [theme.breakpoints.up('lg')]: {
            width: '80%',
            maxWidth: '80%'
        }
    }
}))

export default useStyles
