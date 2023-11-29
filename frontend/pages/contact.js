import {
  Container,
  Grid,
  Typography,
  Link,
  Box,
  Stack,
  Breadcrumbs
} from '@mui/material'
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'
import { useRouter } from 'next/router'
import useStyles from '../styles/pages/contact'
import { parseCookies } from 'nookies'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'

export default function Contact() {
  const router = useRouter()
  const classes = useStyles()

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
          <Box
            sx={{
              mt: 1,
              mb: 1,
              p: 1
            }}
            alignItems="center"
            justifyContent="space-between"
          >
            <Stack
              direction="row"
              justifyContent="flex-start"
              alignItems="center"
              spacing={2}
            >
              <ArrowBackIosIcon
                onClick={() => {
                  router.back()
                }}
                sx={{ cursor: 'pointer' }}
              />
              <Typography variant="h6" sx={{ mb: 2 }}>
                Contact
              </Typography>
            </Stack>
          </Box>
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
                  BRA-LIN S2 Contribution Lead: julia at linea dot org dot br
                </p>
                <p>Technical support: helpdesk at linea dot org dot br</p>
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
