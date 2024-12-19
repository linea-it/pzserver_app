import React, { useState } from 'react'
import InfoIcon from '@mui/icons-material/Info'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import Link from '@mui/material/Link'
import Paper from '@mui/material/Paper'
import Snackbar from '@mui/material/Snackbar'
import SnackbarContent from '@mui/material/SnackbarContent'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useTheme } from '@mui/system'
import SearchField from '../components/SearchField'
import SpeczData from '../components/SpeczData'

function SpeczCatalogs() {
  const theme = useTheme()

  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [search, setSearch] = useState('')
  const filters = useState()
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [initialData, setInitialData] = useState({
    param: {
      crossmatch: {
        output_catalog_name: 'tsm_cross_001'
      },
      description: ''
    }
  })
  const [data, setData] = useState(initialData)
  const [fieldErrors, setFieldErrors] = useState({})

  const handleCatalogNameChange = event => {
    setCombinedCatalogName(event.target.value)
  }

  const handleClearForm = () => {
    setCombinedCatalogName('')
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
              output_catalog_name: sanitizedCatalogName
            },
            description: ''
          }
        },
        release: releaseId,
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
            <Typography color="textPrimary">Combine Spec-z Catalogs</Typography>
          </Breadcrumbs>
          <Grid item xs={12}>
            <Typography variant="h4" mb={3} textAlign={'center'}>
              Combine Spec-z Catalogs
              <IconButton
                color="primary"
                aria-label="info"
                title="Creates a single spec-z sample from the multiple spatial cross-matching (all-to-all) of a list of pre-registered individual Spec-z Catalogs."
              >
                <InfoIcon />
              </IconButton>
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              <Typography variant="body1" mr={'16px'}>
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
                title="the product name of the training set that will result from the process and be automatically registered as a new product on the PZ Server."
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
                3. Select the Spec-z Catalogs to include in your sample:
              </Typography>
              <SearchField onChange={query => setSearch(query)} />
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <SpeczData query={search} filters={filters} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" justifyContent="center" mt={2}>
              <Button
                variant="outlined"
                onClick={handleClearForm}
                sx={{ marginRight: '12px' }}
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

export default SpeczCatalogs
