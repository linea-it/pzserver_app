import InfoIcon from '@mui/icons-material/Info'
import Backdrop from '@mui/material/Backdrop'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CircularProgress from '@mui/material/CircularProgress'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import FormControl from '@mui/material/FormControl'
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
import { useRouter } from 'next/router'
import React, { useEffect, useState } from 'react'
import NNeighbors from '../components/NNeighbors'
import SearchField from '../components/SearchField'
import SearchRadius from '../components/SearchRadius'
import TsmData from '../components/TsmData'
import { getPipelineByName } from '../services/pipeline'
import { submitProcess } from '../services/process'
import { getReleases } from '../services/release'

function TrainingSetMaker() {
  const theme = useTheme()
  const [openDialog, setOpenDialog] = useState(false)
  const router = useRouter()
  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [search, setSearch] = useState('')
  const [selectedProductId, setSelectedProductId] = useState(null)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState('')
  const [snackbarColor, setSnackbarColor] = useState(theme.palette.warning.main)
  const [selectedLsstCatalog, setSelectedLsstCatalog] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [releases, setReleases] = useState([])
  const [initialData, setInitialData] = useState({
    param: {
      crossmatch: {
        n_neighbors: 1,
        radius_arcsec: 1,
        output_catalog_name: 'tsm_cross_001'
      },
      duplicate_criteria: 'closest'
    }
  })
  const [data, setData] = useState(initialData)
  const [fieldErrors] = useState({})

  useEffect(() => {
    const fetchPipelineData = async () => {
      try {
        const response = await getPipelineByName({ name: 'training_set_maker' })
        const pipelineData = response.data.results[0]

        setInitialData(pipelineData)
        setData(pipelineData.system_config)
      } catch (error) {
        console.error('Error fetching pipeline data from API', error)
      }
    }

    const fetchReleases = async () => {
      try {
        const releasesData = await getReleases()

        if (Array.isArray(releasesData.results)) {
          const fetchedReleases = releasesData.results
          setReleases(fetchedReleases)

          if (fetchedReleases.length > 0) {
            setSelectedLsstCatalog(fetchedReleases[0].name)
          }
        } else {
          console.error('No results found in the API response')
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
    setData(initialData.system_config)
    setSelectedLsstCatalog('')
    setIsSubmitting(false)
  }

  const handleDialogClose = () => {
    setOpenDialog(false)
    router.push('/user_products')
  }

  const handleRun = async () => {
    setIsSubmitting(true)

    if (combinedCatalogName.trim() === '') {
      setSnackbarMessage(
        'Your process has not been submitted. Please fill in the training set name.'
      )
      setSnackbarColor(theme.palette.warning.main)
      setSnackbarOpen(true)
      return
    }

    const sanitizedCatalogName = combinedCatalogName
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim()
      .replace(/[\s*,\-*/]+/g, '_')

    try {
      const pipelineId = initialData.id

      const selectedRelease = releases.find(
        release => release.name === selectedLsstCatalog
      )
      const releaseId = selectedRelease ? selectedRelease.id : null

      if (!releaseId) {
        setSnackbarMessage('No valid release selected.')
        setSnackbarColor(theme.palette.error.main)
        setSnackbarOpen(true)
        return
      }

      // Create the JSON object
      const processData = {
        display_name: sanitizedCatalogName,
        pipeline: pipelineId,
        used_config: {
          param: {
            crossmatch: {
              n_neighbors: data.param.crossmatch.n_neighbors,
              radius_arcsec: data.param.crossmatch.radius_arcsec,
              output_catalog_name: sanitizedCatalogName
            },
            duplicate_criteria: data.param.duplicate_criteria
          }
        },
        release: releaseId,
        description: data.param.description,
        inputs: [selectedProductId]
      }

      // tentativa de envio do json via POST
      setIsLoading(true)
      await submitProcess(processData)
      setSnackbarMessage('')
      handleClearForm()
      setOpenDialog(true)
    } catch (error) {
      console.error('Error submitting the process:', error)
      setSnackbarMessage('There was an error submitting your process.')
      setSnackbarColor(theme.palette.error.main)
      setSnackbarOpen(true)
    } finally {
      setIsSubmitting(false)
      setIsLoading(false)
    }
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
    setIsSubmitting(false)
  }

  const handleInputValue = event => {
    const { name, value } = event.target
    setData(prevData => ({
      ...prevData,
      param: {
        ...prevData.param,
        [name]: value
      }
    }))
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
            <Typography variant="body1" mr={'16px'} mb={1}>
              2. Description (optional):
            </Typography>
            <FormControl sx={{ width: '60%' }}>
              <TextField
                name="description"
                label="Description"
                multiline
                minRows={3}
                value={data.param.description}
                onChange={handleInputValue}
                onBlur={handleInputValue}
                error={!!fieldErrors.description}
                helperText={fieldErrors.description}
                sx={{
                  '& .MuiInputBase-root': {
                    height: 'auto'
                  }
                }}
              />
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              <Typography variant="body1" mb={1}>
                3. Select the Spec-z Catalog for the cross-matching:
              </Typography>
              <SearchField onChange={query => setSearch(query)} />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <TsmData
                  query={search}
                  onProductSelect={setSelectedProductId}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              4. Select the Objects catalog (photometric data):
              <Select
                value={selectedLsstCatalog}
                onChange={event => setSelectedLsstCatalog(event.target.value)}
                sx={{ marginLeft: '16px' }}
              >
                {releases.map(release => (
                  <MenuItem key={release.id} value={release.name}>
                    {release.display_name}
                  </MenuItem>
                ))}
              </Select>
            </Typography>
          </Grid>

          <Grid item xs={12} mt={3}>
            <Typography variant="body1">
              5. Select the cross-matching configuration choices:
            </Typography>
            <Grid item xs={12} mt={2}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  The threshold distance in arcseconds beyond which neighbors
                  are not added:
                </Typography>
                <SearchRadius
                  searchRadius={data.param.crossmatch.radius_arcsec}
                  onChange={value => {
                    setData({
                      ...data,
                      param: {
                        ...data.param,
                        crossmatch: {
                          ...data.param.crossmatch,
                          radius_arcsec: value
                        }
                      }
                    })
                  }}
                />
              </Box>
            </Grid>

            <Grid item xs={12} mt={3}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  The number of neighbors to find within each point:
                </Typography>
                <NNeighbors
                  nNeighbors={data.param.crossmatch.n_neighbors}
                  onChange={value => {
                    setData({
                      ...data,
                      param: {
                        ...data.param,
                        crossmatch: {
                          ...data.param.crossmatch,
                          n_neighbors: value
                        }
                      }
                    })
                  }}
                  reset={false}
                />
              </Box>
            </Grid>

            <Grid item xs={12} mt={3}>
              <Box ml={4}>
                In case of multiple spec-z measurements for the same object:
                <Select
                  value={data.param.duplicate_criteria}
                  onChange={e => {
                    setData({
                      ...data,
                      param: {
                        ...data.param,
                        duplicate_criteria: e.target.value
                      }
                    })
                  }}
                  sx={{ ml: '16px' }}
                >
                  <MenuItem value="closest">Keep the closest only</MenuItem>
                  <MenuItem value="all">Keep all</MenuItem>
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

        <Backdrop
          sx={theme => ({ color: '#fff', zIndex: theme.zIndex.drawer + 1 })}
          open={isLoading}
        >
          <CircularProgress color="inherit" />
        </Backdrop>

        <Dialog open={openDialog} onClose={handleDialogClose}>
          <DialogContent>
            <DialogContentText>
              Your process has been submitted successfully.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose} autoFocus>
              OK
            </Button>
          </DialogActions>
        </Dialog>

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
