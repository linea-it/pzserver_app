// TrainingSetMaker.jsx
import * as React from 'react'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'
import Link from '../components/Link'

function TrainingSetMaker() {
  return (
    <Link href="/training_set_maker">
      <Card sx={{ display: 'flex', flexDirection: 'row-reverse' }}>
        <CardMedia
          component="img"
          sx={{ width: 350 }}
          image="../interfaces/lsst_summit.jpg"
          alt="Training Set Maker"
        />
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <CardContent m={2} sx={{ maxWidth: 500 }}>
            <Typography variant="h5">Training Set Maker</Typography>
            <Typography variant="body1" color="text.secondary">
              Creates a training set from the spatial cross-matching of a given
              spec-z catalog and the LSST Objects Catalogs.
            </Typography>
          </CardContent>
        </Box>
      </Card>
    </Link>
  )
}

export default TrainingSetMaker
