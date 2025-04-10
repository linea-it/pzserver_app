import { useState, useEffect } from 'react'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Typography from '@mui/material/Typography'
import Container from '@mui/material/Container'
import Link from '@mui/material/Link'
import Grid from '@mui/material/Grid'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'

import { parseCookies } from 'nookies'
import useStyles from '../styles/pages/about'
import Partnersfooter from '../components/Partnersfooter'

export default function About() {
  const classes = useStyles()
  const [email, setEmail] = useState('')

  useEffect(() => {
    setEmail('helpdesk@linea.org.br')
  }, [])

  return (
    <Container className={classes.root}>
      <Grid container spacing={8}>
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">About</Typography>
          </Breadcrumbs>
          <Typography variant="h6" sx={{ mb: 2 }}>
            About
          </Typography>
          <Card>
            <CardContent>
              <Typography
                variant="body1"
                component="span"
                sx={{ textAlign: 'justify', display: 'block' }}
              >
                <p>
                  Inspired by features of the DES Science Portal (
                  <Link
                    href="https://www.sciencedirect.com/science/article/abs/pii/S2213133718300891?via%3Dihub"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Gschwend et al., 2018;
                  </Link>{' '}
                  <Link
                    href="https://www.sciencedirect.com/science/article/abs/pii/S2213133717300975"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Fausti Neto et al., 2018
                  </Link>{' '}
                  ), the Photo-z Server is an online service, complementary to
                  the Rubin Science Platform (RSP), to host photo-z-related
                  lightweight data products and to offer data management tools
                  that allow sharing data products among RSP users, attach and
                  share relevant metadata, and help on provenance tracking. It
                  is delivered as part of the in-kind contribution program
                  BRA-LIN. An overview of this and other contributions is
                  available{' '}
                  <Link
                    href="https://linea-it.github.io/pz-lsst-inkind-doc/"
                    target="_blank"
                    rel="noreferrer"
                  >
                    here.
                  </Link>{' '}
                  As required by the LSST in-kind program, the source code is
                  publicly available on{' '}
                  <Link
                    href="https://github.com/linea-it/pz-server"
                    target="_blank"
                    rel="noreferrer"
                  >
                    GitHub.
                  </Link>
                </p>
                <p>
                  The Photo-z Server is hosted in the Brazilian Independent Data
                  Access Center (IDAC) and is open to all RSP users (LSST data
                  rights holders), without geographic constraints. It is
                  designed to be as broad and generic as possible to be useful
                  to all LSST Science Collaborations that work with photo-z data
                  products.
                </p>
                <p>
                  The Photo-z Server is being designed with a special focus on
                  helping RSP users participating in the Photo-z Validation
                  Cooperative, a DM team&apos;s initiative that will take place
                  during LSST commissioning phase (see technical note{' '}
                  <Link
                    href="https://dmtn-049.lsst.io/"
                    target="_blank"
                    rel="noreferrer"
                  >
                    dmtn-049
                  </Link>{' '}
                  for details), but it is planned to continue serving the LSST
                  Community during subsequent years. During the Photo-z
                  Validation Cooperative, the Photo-z Coordination Group will be
                  able to use the Photo-z Server to host and distribute
                  standardized training and validation sets to be used in
                  algorithm performance comparison experiments, as well as to
                  collect the results obtained by different users.
                </p>
                <p>
                  Beyond the Photo-z Validation Cooperative, the RSP users will
                  be able to use the Photo-z Server to easily keep track and
                  share lightweight files containing varied test results. All
                  data products uploaded to the Photo-z Server will
                  automatically be visible and available, without any scientific
                  validation, to all RSP users, and only for this particular
                  group, therefore it is not the appropriate tool to release
                  data products to the general public.
                </p>
                <p>
                  If you have comments or suggestions, be welcome to open an
                  issue on the{' '}
                  <Link
                    href="https://github.com/linea-it/pz-server/issues/new"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Photo-z Server repository on GitHub
                  </Link>
                  , or contact the developers at{' '}
                  {email && (
                    <Link
                      href={`mailto:${email}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {email}
                    </Link>
                  )}
                  .
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
