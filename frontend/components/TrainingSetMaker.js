import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'

function TrainingSetMaker() {
  return (
    // <Link href="/training_set_maker">
    <Card
      elevation={3}
      sx={{
        display: 'flex',
        flexDirection: 'row-reverse'
      }}
    >
      <CardMedia
        component="img"
        sx={{ width: 350, height: 231 }}
        image="../interfaces/lsst_summit.jpg"
        alt="Training Set Maker"
      />
      <Box>
        <CardContent m={2} sx={{ maxWidth: 500 }}>
          <Typography color="#888" variant="h5">
            Training Set Maker (soon)
          </Typography>
          <Typography variant="body1" color="#555" sx={{ mt: 1 }}>
            Creates a training set from the spatial cross-matching of a given
            Redshift Catalog and the LSST Objects Catalogs.
          </Typography>
        </CardContent>
      </Box>
    </Card>
    // </Link>
  )
}

export default TrainingSetMaker
