import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(theme => ({
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    },
    content: {
        textAlign: 'center',
    },
    message: {
        color: theme.palette.text.secondary,
    },
}))

export default useStyles
