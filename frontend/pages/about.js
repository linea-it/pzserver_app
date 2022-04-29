import { Container, Grid, Typography } from '@mui/material'

export default function About() {
  return (
    <Container>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h2">About!</Typography>
        </Grid>
      </Grid>
    </Container>
  )
}
