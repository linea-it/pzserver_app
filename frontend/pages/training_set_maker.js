import InfoIcon from '@mui/icons-material/Info'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import MenuItem from '@mui/material/MenuItem'
import Paper from '@mui/material/Paper'
import Select from '@mui/material/Select'
import Snackbar from '@mui/material/Snackbar'
import SnackbarContent from '@mui/material/SnackbarContent'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import React, { useState } from 'react'
import EmailField from '../components/EmailField'
import SearchField from '../components/SearchField'
import SearchRadius from '../components/SearchRadius'
import TsmData from '../components/TsmData'
import useStyles from '../styles/pages/products'

function TrainingSetMaker() {
  const classes = useStyles()

  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [search, setSearch] = React.useState('')
  const filters = React.useState()
  const [selectedSpeczCatalogs, setSelectedTrainingSet] = useState([])
  const [searchRadius, setSearchRadius] = useState('1.0')
  const [selectedOption, setSelectedOption] = useState('pickOne')
  const [email, setEmail] = useState('')
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [selectedLsstCatalog, setSelectedLsstCatalog] = useState('DP0.2')

  const handleCatalogNameChange = event => {
    setCombinedCatalogName(event.target.value)
  }

  const handleSpeczCatalogsChange = event => {
    setSelectedTrainingSet(event.target.value)
  }

  const handleSearchRadiusChange = event => {
    const newValue = parseFloat(event.target.value)
    setSearchRadius(isNaN(newValue) ? '' : newValue.toString())
  }

  const handleLsstCatalogChange = event => {
    setSelectedLsstCatalog(event.target.value)
  }

  const handleEmailChange = newEmail => {
    setEmail(newEmail)
  }

  const handleClearForm = () => {
    setCombinedCatalogName('')
    setSelectedTrainingSet([])
    setSearchRadius('1.0')
    setSelectedOption('pickOne')
    setEmail('')
    setSelectedLsstCatalog('DP0.2')
  }

  const handleRun = () => {
    setSnackbarOpen(true)
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
  }
  return (
    <Paper className={classes.root}>
      <CardContent>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h4" sx={{ textAlign: 'center' }}>
              Training Set Maker
              <IconButton
                color="primary"
                aria-label="info"
                title="Creates a training set from the spatial cross-matching of a given Spec - z Catalog and the LSST Objects Catalogs.Training Set Maker"
              >
                <InfoIcon />
              </IconButton>
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              <Typography variant="body1" sx={{ mr: '16px' }}>
                1. Combined catalog name:
              </Typography>
              <TextField
                id="combinedCatalogName"
                variant="outlined"
                value={combinedCatalogName}
                onChange={handleCatalogNameChange}
              />
              <IconButton
                color="primary"
                aria-label="info"
                title="the product name of the catalog that will result from the process and be automatically registered as a new product on the PZ Server."
              >
                <InfoIcon />
              </IconButton>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1" mb={1}>
              2. Select the Spec-z Catalogs to include in your sample:
            </Typography>
            <Box display="flex">
              <Select
                multiple
                value={selectedSpeczCatalogs}
                onChange={handleSpeczCatalogsChange}
                sx={{ marginRight: '16px', height: '0', marginTop: '8px' }}
              >
                <MenuItem value="name">name</MenuItem>
                <MenuItem value="uploadby">upload by</MenuItem>
                <MenuItem value="createdat">created at</MenuItem>
              </Select>
              <IconButton
                color="primary"
                aria-label="info"
                title="Select the column you want to filter"
              >
                <InfoIcon />
              </IconButton>
              <SearchField onChange={query => setSearch(query)} />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <TsmData query={search} filters={filters} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              3. Select the LSST objects catalog:
              <Select
                value={selectedLsstCatalog}
                onChange={handleLsstCatalogChange}
                sx={{ marginLeft: '16px' }}
              >
                <MenuItem value="DP0.2">DP0.2</MenuItem>
                <MenuItem value="DP1">DP1</MenuItem>
                <MenuItem value="DP2">DP2</MenuItem>
              </Select>
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              4. Select the cross-matching configuration choices:
              <Grid item xs={12}>
                <span>Search Radius (arcsec):</span>{' '}
                <SearchRadius
                  searchRadius={searchRadius}
                  onChange={handleSearchRadiusChange}
                />
              </Grid>
              <Grid item xs={12}>
                <span>
                  In case of multiple spec-z measurements for the same object:
                </span>{' '}
                <Select
                  value={selectedOption}
                  onChange={event => setSelectedOption(event.target.value)}
                  sx={{ marginRight: '10px' }}
                >
                  <MenuItem value="pickOne">Keep the closet only</MenuItem>
                  <MenuItem value="keepAll">Keep all</MenuItem>
                  <MenuItem value="computeMean">
                    Compute mean redshift all candidates
                  </MenuItem>
                </Select>
              </Grid>
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              5. Enter an email address to be notified when the process is
              complete (opcional):
            </Typography>
            <EmailField
              initialValue={email}
              onEmailChange={handleEmailChange}
            />
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" justifyContent="center" mt={2}>
              <Button
                variant="outlined"
                onClick={handleClearForm}
                sx={{ marginRight: '16px' }}
              >
                Clear form
              </Button>
              <Button variant="contained" onClick={handleRun}>
                Run
              </Button>
            </Box>
          </Grid>
        </Grid>
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={6000}
          onClose={handleSnackbarClose}
        >
          <SnackbarContent
            message={`Your process has been submitted successfully. The combined spec-z catalog will be registered soon as: ${combinedCatalogName}`}
          />
        </Snackbar>
      </CardContent>
    </Paper>
  )
}

export default TrainingSetMaker
