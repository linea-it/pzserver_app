import { Typography } from '@mui/material'
import * as React from 'react'
import useStyles from '../styles/pages/training_set_maker'

export default function TrainingSetMaker() {
  const classes = useStyles()

  return (
    <div className={classes.container}>
      <Typography variant="h5" className={classes.message}>
        Coming Soon...
      </Typography>
    </div>
  )
}
