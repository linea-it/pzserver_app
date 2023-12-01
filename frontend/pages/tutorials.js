import Breadcrumbs from '@mui/material/Breadcrumbs'
import Typography from '@mui/material/Typography'
import Container from '@mui/material/Container'
import Link from '@mui/material/Link'
import Grid from '@mui/material/Grid'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Divider from '@mui/material/Divider'

import { parseCookies } from 'nookies'
import useStyles from '../styles/pages/tutorials'

export default function Tutorials() {
  const classes = useStyles()

  return (
    <Container className={classes.root}>
      <Grid container spacing={8}>
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">Tutorials</Typography>
          </Breadcrumbs>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Tutorials
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="h6">Download</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  To download a data product available on the Photo-z Server, go
                  to one of the two pages by clicking on the card &quot;Rubin
                  Observatory PZ Data Products&quot; (for official products
                  released by LSST DM Team) or &quot;User-generated Data
                  Products&quot; (for products uploaded by the members of LSST
                  community. The download button is on the left side of each
                  data product (each row of the list).
                </p>
              </Typography>
              <Typography variant="h6">Upload</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  To upload a data product, click on the button{' '}
                  <strong>&quot;NEW PRODUCT&quot;</strong> on the top left of
                  the <strong>&quot;User-generated Data Products&quot;</strong>{' '}
                  page and fill in the Upload Form with relevant metadata.
                </p>
                <p>
                  The photo-z-related products are organized into four
                  categories (product types):
                </p>
                <ul>
                  <li>
                    <strong>Spec-z Catalog</strong>: Catalog of spectroscopic
                    redshifts and positions (usually equatorial coordinates).
                  </li>
                  <li>
                    <strong>Training Set</strong>: Training set for photo-z
                    algorithms (tabular data). It usually contains magnitudes,
                    errors, and true redshifts.
                  </li>
                  <li>
                    <strong>Photo-z Validation Results</strong>: Results of a
                    photo-z validation procedure (free format). Usually contains
                    photo-z estimates (single estimates and/or pdf) of a
                    validation set, photo-z validation metrics, validation
                    plots, etc.
                  </li>
                  <li>
                    <strong>Photo-z Table</strong>: Results of a photo-z
                    estimation procedure. Ideally in the same format as the
                    photo-z tables delivered by the DM as part of the LSST data
                    releases. If the data is larger than the file upload limit
                    (200MB), the product entry stores only the metadata (and
                    instructions on accessing the data should be provided in the
                    description field).
                  </li>
                </ul>
              </Typography>
              <Typography variant="h6">Access via API</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  The registered data products can also be accessed directly
                  from Python code using the PZ Server&apos;s data access API.
                  The internal documentation of the API functions is available
                  on the{' '}
                  <Link
                    href="https://linea-it.github.io/pzserver"
                    target="_blank"
                    rel="noreferrer"
                  >
                    API&apos;s documentation page
                  </Link>
                  .
                </p>
                <p>
                  <strong>Instalation via pip</strong>
                </p>
                <p>
                  The PZ Server API is avalialble as a Python library on pip as{' '}
                  <strong>pzserver</strong>. To install the API and its
                  dependencies, type, on the Terminal:
                </p>
                <pre className={classes.codeBlock}>
                  <code>$ pip install pzserver </code>
                </pre>
                <p>
                  <strong>Repository clone</strong>
                </p>
                <p>Alternatively, if you have cloned the repository with:</p>
                <pre className={classes.codeBlock}>
                  <code>
                    $ git clone https://github.com/linea-it/pzserver.git
                  </code>
                </pre>
                <p>To install the API and its dependencies, type:</p>
                <pre className={classes.codeBlock}>
                  <code>$ python setup.py install</code>
                </pre>
                <p></p>
              </Typography>
              <Typography variant="h6">Tutorial notebook</Typography>
              <Divider />
              <Typography variant="body1" component="span">
                <p>
                  A Jupyter Notebook with instructions and use-case examples is
                  available also in the{' '}
                  <Link
                    href="https://github.com/linea-it/pzserver/blob/main/notebooks/pz_server_tutorial.ipynb"
                    target="_blank"
                    rel="noreferrer"
                  >
                    library&apos;s repository on Github
                  </Link>
                  .
                </p>
              </Typography>
            </CardContent>
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
