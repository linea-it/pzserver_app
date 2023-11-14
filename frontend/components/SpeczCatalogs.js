// SpeczCatalogs.jsx
import * as React from 'react'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'
import Link from '../components/Link'

function SpeczCatalogs() {
  return (
    <Link href="/specz_catalogs">
      <Card sx={{ display: 'flex' }}>
        <CardMedia
          component="img"
          sx={{ width: 350 }}
          image="../interfaces/milkyway.jpg"
          alt="Spec-z Catalogs"
        />
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <CardContent m={2} sx={{ maxWidth: 500 }}>
            <Typography variant="h5">Combine Spec-z Catalogs</Typography>
            <Typography variant="body1" color="text.secondary">
              Creates a single spec-z from the multiple spatial cross-matching
              (all-to-all) of a list of pre-registered individual spec-z
              catalogs.
            </Typography>
          </CardContent>
        </Box>
      </Card>
    </Link>
  )
}

export default SpeczCatalogs
