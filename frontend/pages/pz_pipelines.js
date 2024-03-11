import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import Link from '@mui/material/Link'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import React from 'react'
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
        <Breadcrumbs aria-label="breadcrumb" sx={{ ml: -30 }}>
          <Link color="inherit" href="/">
            Home
          </Link>
          <Typography color="textPrimary">Pipelines</Typography>
        </Breadcrumbs>
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
