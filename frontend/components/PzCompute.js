import * as React from 'react'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'
import Link from './Link'

function PzCompute() {
  return (
    <Link href="/pz_compute">
      <Card
        elevation={3}
        sx={{
          display: 'flex'
        }}
      >
        <CardMedia
          component="img"
          sx={{ width: 350 }}
          image="../interfaces/telescope.jpg"
          alt="PhotozCompute"
        />
        <Box>
          <CardContent m={2} sx={{ maxWidth: 500 }}>
            <Typography variant="h5">Photo-z Compute</Typography>
            <Typography variant="body1" color="text.secondary">
              A high-performance computing pipeline to estimate photo-zs using
              the Brazilian IDAC resources.
            </Typography>
          </CardContent>
        </Box>
      </Card>
    </Link>
  )
}

export default PzCompute
