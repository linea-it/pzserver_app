import React from 'react'
import { Grid, Typography } from '@mui/material'
import SpeczCatalogs from '../components/SpeczCatalogs'
import TrainingSetMaker from '../components/TrainingSetMaker'

function PZPipelines() {
  return (
    <Grid container direction="column" alignItems="center">
      <Typography
        variant="h4"
        align="center"
        color="textPrimary"
        mb={10}
        mt={-12}
      >
        Photo-z Server Pipelines
      </Typography>

      <Grid item mb={5}>
        <SpeczCatalogs />
      </Grid>
      <Grid item>
        <TrainingSetMaker />
      </Grid>
    </Grid>
  )
}

export default PZPipelines
