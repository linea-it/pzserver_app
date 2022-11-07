import { Container, Grid, Typography, Link } from '@mui/material'
import useStyles from '../styles/pages/contact'
import { parseCookies } from 'nookies'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
export default function Contact() {
  const classes = useStyles()
  return (
    <Container className={classes.root}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Contact
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="body1" component="span">
                <p>Comments, questions, suggestions?</p>
                <p>
                  Be welcome to open an issue on the{' '}
                  <Link
                    href="https://github.com/linea-it/pz-server"
                    target="_blank"
                    rel="noreferrer"
                  >
                    PZ Server repository on GitHub
                  </Link>
                  , or contact our team.
                </p>
                <p>
                  BRA-LIN S2 Contribution Lead:{' '}
                  <Link
                    href="mailto:julia@linea.org.br"
                    target="_blank"
                    rel="noreferrer"
                  >
                    julia@linea.org.br
                  </Link>
                </p>
                <p>
                  Technical support:{' '}
                  <Link
                    href="mailto:helpdesk@linea.org.br"
                    target="_blank"
                    rel="noreferrer"
                  >
                    helpdesk@linea.org.br
                  </Link>
                </p>
              </Typography>
            </CardContent>{' '}
          </Card>
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
