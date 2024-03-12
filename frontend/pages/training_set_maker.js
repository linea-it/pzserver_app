import React from 'react'
import { Typography, Box } from '@mui/material'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Link from '@mui/material/Link'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import InfoIcon from '@mui/icons-material/Info'
import ArrowBackIos from '@mui/icons-material/ArrowBackIos'

function TrainingSetMaker() {
  return (
    <Grid flexGrow={1} mt={3}>
      <Breadcrumbs aria-label="breadcrumb" ml={1}>
        <Link color="inherit" href="/">
          Home
        </Link>
        <Link color="inherit" href="pz_pipelines">
          Pipelines
        </Link>
        <Typography color="textPrimary">
          Training Set Maker
        </Typography>
      </Breadcrumbs>
      <Grid>
        <Typography variant="h5" textAlign={'left'} ml={1} mt={1}>
          <IconButton
            color="primary"
            aria-label="Go back"
            onClick={() => window.history.back()}
          >
            <ArrowBackIos />
          </IconButton>
          Training Set Maker
          <IconButton
            color="primary"
            aria-label="info"
            title="Creates a training set from the spatial cross-matching of a given Spec - z Catalog and the LSST Objects Catalogs.Training Set Maker"
          >
            <InfoIcon />
          </IconButton>
        </Typography>
      </Grid>
      <Box textAlign={'center'} mt={30}>
        <Typography variant="h4">Coming soon...</Typography>
      </Box>
    </Grid>
  )
}

export default TrainingSetMaker
