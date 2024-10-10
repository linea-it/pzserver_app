import InfoIcon from '@mui/icons-material/Info'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import Link from '@mui/material/Link'
import MenuItem from '@mui/material/MenuItem'
import Paper from '@mui/material/Paper'
import Select from '@mui/material/Select'
import Snackbar from '@mui/material/Snackbar'
import SnackbarContent from '@mui/material/SnackbarContent'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useTheme } from '@mui/system'
import React, { useEffect, useState } from 'react'
import NNeighbors from '../components/NNeighbors'
import SearchField from '../components/SearchField'
import SearchRadius from '../components/SearchRadius'
import TsmData from '../components/TsmData'
import { getPipeline } from '../services/pipeline'
import { getReleases } from '../services/release'

function TrainingSetMaker() {
  const theme = useTheme()
  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [search, setSearch] = useState('')
  const [searchRadius, setSearchRadius] = useState(1.0)
  const [nNeighbors, setNNeighbors] = useState(1)
  const [selectedOption, setSelectedOption] = useState('closest')
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [selectedLsstCatalog, setSelectedLsstCatalog] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState('')
  const [snackbarColor, setSnackbarColor] = useState(theme.palette.warning.main)
  const [releases, setReleases] = useState([])

  useEffect(() => {
    const fetchPipelineData = async () => {
      try {
        const response = await getPipeline()
        const pipelineData = response.data.results[0].system_config

        const defaultSearchRadius =
          parseFloat(pipelineData.param.crossmatch.radius_arcsec) || 1.0
        const defaultNNeighbors = pipelineData.param.crossmatch.n_neighbors || 1
        const defaultDuplicateCriteria =
          pipelineData.param.duplicate_criteria || 'closest'

        setSearchRadius(Math.min(defaultSearchRadius, 90))
        setNNeighbors(Math.min(defaultNNeighbors, 90))
        setSelectedOption(defaultDuplicateCriteria)
      } catch (error) {
        console.error('Error fetching pipeline data from API', error)
      }
    }

    const fetchReleases = async () => {
      try {
        const response = await getReleases()
        const fetchedReleases = response.data.results
        setReleases(fetchedReleases)

        if (fetchedReleases.length > 0) {
          setSelectedLsstCatalog(fetchedReleases[0].name)
        }
      } catch (error) {
        console.error('Error fetching releases from API', error)
      }
    }

    fetchPipelineData()
    fetchReleases()
  }, [])

  const handleClearForm = () => {
    setCombinedCatalogName('')
    setSearchRadius(1.0)
    setNNeighbors(1)
    setSelectedOption('closest')
    setSelectedLsstCatalog('')
    setIsSubmitting(false)
  }

  const handleRun = () => {
    setIsSubmitting(true)

    if (combinedCatalogName.trim() === '') {
      setSnackbarMessage(
        'Your process has not been submitted. Please fill in the training set name.'
      )
      setSnackbarColor(theme.palette.warning.main)
      setSnackbarOpen(true)
      return
    }

    setSnackbarMessage('Your process has been submitted successfully.')
    setSnackbarColor(theme.palette.success.main)
    setSnackbarOpen(true)
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
    setIsSubmitting(false)
  }

  const styles = {
    root: {
      transition: 'box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) 0ms',
      borderRadius: '4px',
      padding: theme.spacing(3),
      flex: '1 1 0%'
    }
  }

  return (
    <Paper style={styles.root}>
      <CardContent>
        <Grid container spacing={3}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Link color="inherit" href="pz_pipelines">
              Pipelines
            </Link>
            <Typography color="textPrimary">Training Set Maker</Typography>
          </Breadcrumbs>

          <Grid item xs={12}>
            <Typography variant="h4" mb={3} textAlign="center">
              Training Set Maker
              <IconButton
                color="primary"
                aria-label="info"
                title="Creates a training set from the spatial cross-matching of a given Spec - z Catalog and the LSST Objects Catalogs."
              >
                <InfoIcon />
              </IconButton>
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              <Typography variant="body1" mr="16px">
                1. Training set name:
                <Typography component="span" sx={{ color: 'red' }}>
                  *
                </Typography>
              </Typography>
              <TextField
                id="combinedCatalogName"
                variant="outlined"
                value={combinedCatalogName}
                onChange={event => setCombinedCatalogName(event.target.value)}
                error={isSubmitting && combinedCatalogName.trim() === ''}
                helperText={
                  isSubmitting && combinedCatalogName.trim() === ''
                    ? 'This field is required.'
                    : ''
                }
              />
              <IconButton
                color="primary"
                aria-label="info"
                title="Name to be displayed on the products list"
              >
                <InfoIcon />
              </IconButton>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              <Typography variant="body1" mb={1}>
                2. Select the Spec-z Catalog for the cross-matching:
              </Typography>
              <SearchField onChange={query => setSearch(query)} />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <TsmData query={search} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              3. Select the Objects catalog (photometric data):
              <Select
                value={selectedLsstCatalog} // Certifique-se de que isso está sendo atualizado corretamente
                onChange={event => setSelectedLsstCatalog(event.target.value)}
                sx={{ marginLeft: '16px' }}
              >
                {releases.map(release => (
                  <MenuItem key={release.id} value={release.name}>
                    {release.display_name} {/* Exibe o nome correto */}
                  </MenuItem>
                ))}
              </Select>
            </Typography>
          </Grid>

          <Grid item xs={12} mt={3}>
            <Typography variant="body1">
              4. Select the cross-matching configuration choices:
            </Typography>
            <Grid item xs={12} mt={2}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  The threshold distance in arcseconds beyond which neighbors
                  are not added:
                </Typography>
                <SearchRadius
                  searchRadius={searchRadius}
                  onChange={setSearchRadius}
                />
              </Box>
            </Grid>

            <Grid item xs={12} mt={3}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  The number of neighbors to find within each point:
                </Typography>
                <NNeighbors
                  nNeighbors={nNeighbors}
                  onChange={setNNeighbors}
                  reset={false}
                />
              </Box>
            </Grid>

            <Grid item xs={12} mt={3}>
              <Box ml={4}>
                In case of multiple spec-z measurements for the same object:
                <Select
                  value={selectedOption}
                  onChange={event => setSelectedOption(event.target.value)}
                  sx={{ ml: '16px' }}
                >
                  <MenuItem value="closest">Keep the closest only</MenuItem>
                  <MenuItem value="keepAll">Keep all</MenuItem>
                </Select>
              </Box>
            </Grid>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" justifyContent="center" mt={2}>
              <Button variant="outlined" onClick={handleClearForm}>
                Clear form
              </Button>
              <Button variant="contained" onClick={handleRun} sx={{ ml: 2 }}>
                Run
              </Button>
            </Box>
          </Grid>
        </Grid>

        <Snackbar
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          open={snackbarOpen}
          onClose={handleSnackbarClose}
        >
          <SnackbarContent
            message={snackbarMessage}
            style={{ backgroundColor: snackbarColor }}
          />
        </Snackbar>
      </CardContent>
    </Paper>
  )
}

export default TrainingSetMaker
