import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import Link from '@mui/material/Link'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import ArrowBackIos from '@mui/icons-material/ArrowBackIos'
import IconButton from '@mui/material/IconButton'
import React from 'react'
import SpeczCatalogs from '../components/SpeczCatalogs'
import TrainingSetMaker from '../components/TrainingSetMaker'
// import PzCompute from '../components/PzCompute'

function PZPipelines() {
  return (
    <Grid container direction="column" alignItems="center" mb={10}>
      <Typography
        variant="h4"
        align="center"
        color="textPrimary"
        mb={5}
        mr={55}
      >
        <Breadcrumbs aria-label="breadcrumb" sx={{ mt: '25px' }}>
          <Link color="inherit" href="/">
            Home
          </Link>
          <Typography color="textPrimary">Pipelines</Typography>
        </Breadcrumbs>
        <IconButton
          color="primary"
          edge="start"
          aria-label="Go back"
          onClick={() => (window.location.href = window.location.origin)}
        >
          <ArrowBackIos />
        </IconButton>
        Photo-z Server Pipelines
      </Typography>

      <Grid item xs={12} mb={5}>
        <SpeczCatalogs />
      </Grid>
      <Grid item xs={12} mb={5}>
        <TrainingSetMaker />
      </Grid>
      {/* <Grid item xs={12}>
        <PzCompute />
      </Grid> */}
    </Grid>
  )
}

export default PZPipelines
