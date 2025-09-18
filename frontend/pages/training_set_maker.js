import Backdrop from '@mui/material/Backdrop'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Checkbox from '@mui/material/Checkbox'
import CircularProgress from '@mui/material/CircularProgress'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
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
import { useEffect, useState } from 'react'
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
  const [uniqueGalaxies, setUniqueGalaxies] = useState(false)
  const [convertFluxToMag, setConvertFluxToMag] = useState(true)
  const [disabledFluxToMag, setDisabledConvertFluxToMag] = useState(false)
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
  const [fluxes, setFluxes] = useState([])
  const [dereddening, setDereddening] = useState([])
  const [outputFormat, setOutputFormat] = useState('specz')
  const [initialData, setInitialData] = useState({
    param: {
      crossmatch: {
        n_neighbors: 1,
        radius_arcsec: 1,
        output_catalog_name: 'tsm_cross_001'
      },
      duplicate_criteria: 'closest',
      flux_type: 'cmodel',
      dereddening: 'sfd',
      convert_flux_to_mag: true
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

          // Remove releases that have neither mag_hats nor flux_hats
          const filteredReleases = fetchedReleases.filter(
            release =>
              release.has_mag_hats === true || release.has_flux_hats === true
          )
          setReleases(filteredReleases)

          if (filteredReleases.length > 0) {
            handleRelease(filteredReleases[0].name, filteredReleases)
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
    setOutputFormat('specz')
    setIsSubmitting(false)
  }

  const handleRelease = (releaseName, releasesData) => {
    setSelectedLsstCatalog(releaseName)

    const releaseList = releasesData || releases
    const currentRelease = releaseList.find(
      release => release.name === releaseName
    )

    if (!currentRelease) return

    if (currentRelease.has_mag_hats === true) {
      setConvertFluxToMag(true)
      if (currentRelease.has_flux_hats) {
        setDisabledConvertFluxToMag(false)
      } else {
        setDisabledConvertFluxToMag(true)
      }
    } else {
      setDisabledConvertFluxToMag(true)
      setConvertFluxToMag(false)
    }

    const fluxRelease = currentRelease.fluxes
    setFluxes(fluxRelease)

    const selectedFlux = fluxRelease.find(flux => flux.selected)
    if (selectedFlux) {
      setData(prevData => ({
        ...prevData,
        param: {
          ...prevData.param,
          flux_type: selectedFlux.name
        }
      }))
    }

    const dereddeningRelease = currentRelease.dereddening
    setDereddening(dereddeningRelease)

    const selectedDereddening = dereddeningRelease.find(der => der.selected)
    if (selectedDereddening) {
      setData(prevData => ({
        ...prevData,
        param: {
          ...prevData.param,
          dereddening: selectedDereddening.name
        }
      }))
    }
  }

  const handleDialogClose = () => {
    setOpenDialog(false)
    router.push('/user_products')
  }

  const handleUniqueGalaxies = event => {
    setUniqueGalaxies(event.target.checked)
  }

  const handleConvertFluxToMag = event => {
    setConvertFluxToMag(event.target.checked)
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
            duplicate_criteria: data.param.duplicate_criteria,
            flux_type: data.param.flux_type,
            dereddening: data.param.dereddening,
            convert_flux_to_mag: convertFluxToMag
          }
        },
        output_format: outputFormat,
        release: releaseId,
        description: data.param.description,
        inputs: [selectedProductId]
      }

      // tentativa de envio do json via POST
      setIsLoading(true)

      console.log('Submitting process data:', processData)

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
            </Typography>
            <Typography variant="p" mb={3} textAlign={'left'}>
              The Training Set Maker pipeline uses LSDB to perform spatial
              cross-matching between a pre-registered Redshift Catalog and the
              LSST Objects catalog in order to create training sets for
              machine-learning based photo-z algorithms.
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
                3. Select the Redshift Catalog for the cross-matching:
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
                onChange={event => handleRelease(event.target.value)}
                sx={{ marginLeft: '16px' }}
              >
                {releases.map(release => (
                  <MenuItem key={release.id} value={release.name}>
                    {release.display_name}
                  </MenuItem>
                ))}
              </Select>
            </Typography>

            <Grid item xs={12} mt={2}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  Flux type:
                  <Select
                    value={data.param.flux_type}
                    onChange={event => {
                      setData({
                        ...data,
                        param: {
                          ...data.param,
                          flux_type: event.target.value
                        }
                      })
                    }}
                    sx={{ marginLeft: '16px' }}
                  >
                    {fluxes.map(flux => (
                      <MenuItem
                        key={flux.name}
                        value={flux.name}
                        selected={!!flux.selected}
                        disabled={!!flux.disabled}
                      >
                        {flux.display_name}
                      </MenuItem>
                    ))}
                  </Select>
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} mt={2}>
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1" mr="16px">
                  Apply dereddening from{' '}
                  <Link
                    color="inherit"
                    underline="always"
                    href="https://dustmaps.readthedocs.io/en/latest/index.html"
                  >
                    dustmaps
                  </Link>
                  :
                  {/* None, sfd, csfd, planck, planckGNILC, bayestar, iphas, marshall, chen2014, lenz2017, leikeensslin2019, leike2020, edenhofer2023, gaia_tge, decaps */}
                  <Select
                    value={data.param.dereddening}
                    onChange={event => {
                      setData({
                        ...data,
                        param: {
                          ...data.param,
                          dereddening: event.target.value
                        }
                      })
                    }}
                    sx={{ marginLeft: '16px' }}
                  >
                    {dereddening.map(der => (
                      <MenuItem
                        key={der.name}
                        value={der.name}
                        selected={!!der.selected}
                        disabled={!!der.disabled}
                      >
                        {der.display_name}
                      </MenuItem>
                    ))}
                  </Select>
                </Typography>
              </Box>
            </Grid>
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
              <Box display="flex" alignItems="center" ml={4}>
                <Typography variant="body1">
                  Convert fluxes into magnitudes:
                  <Checkbox
                    checked={convertFluxToMag}
                    onChange={handleConvertFluxToMag}
                    disabled={!!disabledFluxToMag}
                    inputProps={{ 'aria-label': 'controlled' }}
                  />
                </Typography>
              </Box>
            </Grid>

            {/* <Grid item xs={12} mt={3}>
              <Box ml={4}>
                In case of multiple redshift measurements for the same object:
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
            </Grid> */}
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1" sx={{ color: '#888' }}>
              6. Select unique galaxies
              <Checkbox
                checked={uniqueGalaxies}
                onChange={handleUniqueGalaxies}
                inputProps={{ 'aria-label': 'controlled' }}
                disabled
              />
              <Typography component="span">(soon)</Typography>
            </Typography>
          </Grid>

          <Grid item xs={12} mt={3}>
            <Typography variant="body1">
              7. Output format:
              <Select
                value={outputFormat}
                onChange={event => setOutputFormat(event.target.value)}
                defaultValue="specz"
              >
                <MenuItem value="specz">same as redshift catalog</MenuItem>
                <MenuItem value="csv">csv</MenuItem>
                <MenuItem value="fits">fits</MenuItem>
                <MenuItem value="parquet">parquet</MenuItem>
                <MenuItem value="hdf5">hdf5</MenuItem>
                <MenuItem value="votable" disabled>
                  VOTable
                </MenuItem>
              </Select>
            </Typography>
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
            <DialogContentText sx={{ textAlign: 'center' }}>
              Your process has been submitted successfully. <br />
              The results will appear as a new product on the list soon.
            </DialogContentText>
          </DialogContent>
          <DialogActions sx={{ justifyContent: 'center' }}>
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
