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
      <Card
        elevation={3}
        sx={{
          display: 'flex'
        }}
      >
        <CardMedia
          component="img"
          sx={{ width: 350, height: 231 }}
          image="../interfaces/milkyway.jpg"
          alt="Spec-z Catalogs"
        />
        <Box>
          <CardContent m={2} sx={{ maxWidth: 500 }}>
            <Typography variant="h5">Combine Spec-z Catalogs</Typography>
            <Typography variant="body1" color="text.secondary">
              Creates a single spec-z sample from the multiple spatial
              cross-matching (all-to-all) of a list of pre-registered individual
              Spec-z Catalogs.
            </Typography>
          </CardContent>
        </Box>
      </Card>
    </Link>
  )
}

export default SpeczCatalogs
