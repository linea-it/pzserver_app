import { Container, Grid, Typography } from '@mui/material'
import useStyles from '../styles/pages/tutorials'
import { parseCookies } from 'nookies'
export default function Tutorials() {
  const classes = useStyles()
  return (
    <Container className={classes.root}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h6">Tutorials</Typography>
          <Typography variant="body1" component="span">
            Coming soon!
          </Typography>
        </Grid>
      </Grid>
    </Container>
  )
}

export const getServerSideProps = async ctx => {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (!token) {
    return {
      redirect: {
        destination: '/login',
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
}
