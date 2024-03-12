import React from 'react'
import { Typography, Box } from '@mui/material'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Link from '@mui/material/Link'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import InfoIcon from '@mui/icons-material/Info'
import ArrowBackIos from '@mui/icons-material/ArrowBackIos'

function SpeczCatalogs() {
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
          Combine Spec-z Catalogs
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
          Combine Spec-z Catalogs
          <IconButton
            color="primary"
            aria-label="info"
            title="Creates a single spec-z sample from the multiple spatial cross-matching (all-to-all) of a list of pre-registered individual Spec-z Catalogs."
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

export default SpeczCatalogs
