import React from 'react'
import { Grid, Typography } from '@mui/material'
import useStyles from '../styles/pages/banner'
const Banner = () => {
  const classes = useStyles()

  return (
    <Grid className={classes.banner}>
      <Grid
        container
        direction="row"
        justifyContent="space-between"
        alignItems="flex-start"
        className={classes.container}
      >
        <Grid item xs={12} className={classes.titleWrapper}>
          <Typography variant="h1" className={classes.title}>
            PZ Server Pipelines
          </Typography>
          <Typography variant="body1" display="block">
            <p>
              Pipelines to create customized science-driven PZ-related data
              products.
            </p>
          </Typography>
        </Grid>
      </Grid>
    </Grid>
  )
}

export default Banner
