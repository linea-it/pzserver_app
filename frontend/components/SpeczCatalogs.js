import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'

function SpeczCatalogs() {
  return (
    // <Link href="/specz_catalogs">
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
          <Typography color="#888" variant="h5">
            Combine Redshift Catalogs (soon)
          </Typography>
          <Typography variant="body1" color="#555" sx={{ mt: 1 }}>
            Creates a single redshift sample from the multiple spatial
            cross-matching (all-to-all) of a list of pre-registered individual
            Redshift Catalogs.
          </Typography>
        </CardContent>
      </Box>
    </Card>
    // </Link>
  )
}

export default SpeczCatalogs
