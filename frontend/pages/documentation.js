import Breadcrumbs from '@mui/material/Breadcrumbs'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Grid from '@mui/material/Grid'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import { parseCookies } from 'nookies'
import Partnersfooter from '../components/Partnersfooter'
import useStyles from '../styles/pages/documentation'

export default function Documentation() {
  const classes = useStyles()

  return (
    <Container className={classes.root} sx={{ overflowY: 'hidden' }}>
      <Grid container spacing={8}>
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">Documentation</Typography>
          </Breadcrumbs>
          {/* <Typography variant="h6" sx={{ mb: 2 }}>
            Documentation
          </Typography> */}
          <Card>
            <CardContent>
              <Typography variant="h6">
                Photo-z Server Documentation for Users
              </Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  Please find the complete documentation about how to use the
                  Photo-z Server website, available in English, Spanish, and
                  Brazilian Portuguese on its{' '}
                  <Link
                    href="https://docs.linea.org.br/en/sci-platforms/pz_server.html"
                    target="_blank"
                    rel="noreferrer"
                  >
                    documentation for users web page
                  </Link>
                  .
                </p>
              </Typography>
              <Typography variant="h6">Access via API</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  The registered data products can also be accessed directly
                  from Python code using the PZ Server&apos;s library. The
                  internal documentation of the API functions is available on
                  the{' '}
                  <Link
                    href="https://linea-it.github.io/pzserver"
                    target="_blank"
                    rel="noreferrer"
                  >
                    API&apos;s documentation page
                  </Link>
                  .
                </p>
                <p>Instalation:</p>
                <pre className={classes.codeBlock}>
                  <code>$ pip install pzserver </code>
                </pre>
                <p></p>
              </Typography>
              <Typography variant="h6">Tutorial notebook</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  A tutorial notebook with examples for all pzserver methods is
                  available on{' '}
                  <Link
                    href="https://github.com/linea-it/pzserver/blob/main/docs/notebooks/pzserver_tutorial.ipynb"
                    target="_blank"
                    rel="noreferrer"
                  >
                    it&apos;s repository on Github
                  </Link>
                  .
                </p>
              </Typography>
              <Typography variant="h6">Data Products</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  The photo-z-related products are organized into four
                  categories (product types):
                </p>
                <ul>
                  <li>
                    <strong>Reference Redshift Catalog</strong>: Catalog of
                    reference redshifts and positions of galaxies (usually
                    spectroscopic redshifts and equatorial coordinates).
                  </li>
                  <li>
                    <strong>Training Set</strong>: Training set for photo-z
                    algorithms (tabular data). It usually contains magnitudes,
                    errors, and reference redshifts.
                  </li>
                  <li>
                    <strong>Training Results</strong>: Results of a photo-z
                    training procedure (free format). Usually a pickle file
                    created by RAIL Inform submodule.
                  </li>
                  <li>
                    <strong>Validation Results</strong>: Results of a photo-z
                    validation procedure (free format). Usually contains photo-z
                    estimates (single estimates and/or pdf) of a validation set,
                    photo-z validation metrics, validation plots, etc.
                  </li>
                  <li>
                    <strong>Photo-z Estimates</strong>: Results of a photo-z
                    estimation procedure (usually the output of RAIL Estimate
                    module). If the data is larger than the file upload limit
                    (200MB), the product entry stores only the metadata
                    (instructions on accessing the data should be provided in
                    the description field.
                  </li>
                </ul>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Partnersfooter />
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
