import { Container, Grid, Typography, Link } from '@mui/material'
import useStyles from '../styles/pages/contact'
export default function Contact() {
  const classes = useStyles()
  return (
    <Container className={classes.root}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h6">Contact</Typography>
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
                href="mailto:julia@linea.gov.br"
                target="_blank"
                rel="noreferrer"
              >
                julia@linea.gov.br
              </Link>
            </p>
            <p>
              Technical support:{' '}
              <Link
                href="mailto:helpdesk@linea.gov.br"
                target="_blank"
                rel="noreferrer"
              >
                helpdesk@linea.gov.br
              </Link>
            </p>
          </Typography>
        </Grid>
      </Grid>
    </Container>
  )
}
