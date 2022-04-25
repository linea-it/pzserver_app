import { Container, Grid, Typography } from '@mui/material'

export default function Contact() {
  return (
    <Container>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h2">Contact!</Typography>
        </Grid>
      </Grid>
    </Container>
  )
}
