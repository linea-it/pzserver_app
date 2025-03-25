import { useState, useEffect } from 'react'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Typography from '@mui/material/Typography'
import Container from '@mui/material/Container'
import Link from '@mui/material/Link'
import Grid from '@mui/material/Grid'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'

import { parseCookies } from 'nookies'
import useStyles from '../styles/pages/contact'
import Partnersfooter from '../components/Partnersfooter'

export default function Contact() {
  const classes = useStyles()
  const [emails, setEmails] = useState({})

  useEffect(() => {
    setEmails({
      lead: 'julia@linea.org.br',
      support: 'helpdesk@linea.org.br'
    })
  }, [])

  return (
    <Container className={classes.root}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">Contact</Typography>
          </Breadcrumbs>
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
                  BRA-LIN-S4 Contribution Lead:{' '}
                  {emails.lead ? (
                    <Link href={`mailto:${emails.lead}`}>{emails.lead}</Link>
                  ) : (
                    'Loading...'
                  )}
                </p>
                <p>
                  Technical support:{' '}
                  {emails.support ? (
                    <Link href={`mailto:${emails.support}`}>
                      {emails.support}
                    </Link>
                  ) : (
                    'Loading...'
                  )}
                </p>
              </Typography>
            </CardContent>
          </Card>
          <Partnersfooter />
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
