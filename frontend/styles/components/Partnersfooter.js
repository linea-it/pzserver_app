import { makeStyles } from '@mui/styles'

const useStyles = makeStyles((theme) => ({
    footer: {
        padding: theme.spacing(4, 0)
    },
    footerDivider: {
        width: '100%',
        maxWidth: '1000px',
        height: '0.5px',
        backgroundColor: '#ccc',
        margin: '0 auto',
        marginBottom: theme.spacing(12)
    },
    verticalDivider: {
        height: '110px',
        width: '0.5px',
        backgroundColor: '#ccc',
        margin: '0 auto',
        position: 'relative',
        top: '-80px'
    },
    logoContainer: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-start',
        paddingLeft: theme.spacing(4)
    },
    address: {
        fontSize: '14px',
        color: '#000',
        paddingLeft: theme.spacing(10)
    },
    futureText: {
        mT: '32px',
        background: '-webkit-linear-gradient(120deg, #0989cb, #31297f)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontSize: '16px',
        fontWeight: 'normal',
        textAlign: 'left',
        paddingLeft: theme.spacing(5),
        wordSpacing: '0.8rem',
        mB: '10px'
    },
    partnerSection: {
        textAlign: 'left',
        marginBottom: theme.spacing(2)
    },
    apoioText: {
        color: '#a3a3a3',
        fontSize: '.9rem',
        textAlign: 'left'
    },
    partnerLogo: {
        width: '100px',
        height: '60px',
        margin: theme.spacing(1),
        filter: 'grayscale(100%)',
        transition: 'filter 0.3s ease',
        '&:hover': {
            filter: 'grayscale(0%)'
        }
    },
    inctLogo: {
        width: '60px',
        height: '60px',
        margin: theme.spacing(1.5),
        filter: 'grayscale(100%)',
        transition: 'filter 0.3s ease',
        '&:hover': {
            filter: 'grayscale(0%)'
        }
    },
    contactSection: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: theme.spacing(6)
    },
    socialIcons: {
        marginTop: theme.spacing(1),
        display: 'flex',
        justifyContent: 'center'
    },
    socialIcon: {
        width: '68px',
        height: '48px'
    },
    linkedinHover: {
        '&:hover': {
            color: '#0077B5'
        }
    },
    instagramHover: {
        '&:hover': {
            color: '#E1306C'
        }
    },
    youtubeHover: {
        '&:hover': {
            color: '#FF0000'
        }
    },
    facebookHover: {
        '&:hover': {
            color: '#1877F2'
        }
    },
    bottomText: {
        textAlign: 'center',
        color: '#a3a3a3',
        fontSize: '0.875rem'
    },
}))

export default useStyles
