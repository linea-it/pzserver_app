import { Container, Grid, Typography } from '@material-ui/core'

export default function Tutorials() {
  return (
    <Container>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h2">Tutorials!</Typography>
        </Grid>
      </Grid>
    </Container>
  )
}
