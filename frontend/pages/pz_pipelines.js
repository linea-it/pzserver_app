import { Typography } from '@mui/material'
import * as React from 'react'
import useStyles from '../styles/pages/pz_pipelines'

export default function PZPipelines() {
  const classes = useStyles()

  return (
    <div className={classes.container}>
      <Typography variant="h5" className={classes.message}>
        Coming Soon...
      </Typography>
    </div>
  )
}
