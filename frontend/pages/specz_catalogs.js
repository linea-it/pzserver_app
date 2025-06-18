import InfoIcon from '@mui/icons-material/Info'
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
import { useEffect, useState } from 'react'
import SearchField from '../components/SearchField'
import SpeczData from '../components/SpeczData'
import { getPipelineByName } from '../services/pipeline'
import { submitProcess } from '../services/process'

function SpeczCatalogs() {
  const theme = useTheme()

  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [uniqueGalaxies, setUniqueGalaxies] = useState(false)
  const [search, setSearch] = useState('')
  const router = useRouter()
  const [filters] = useState({})
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [openDialog, setOpenDialog] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState('')
  const [snackbarColor, setSnackbarColor] = useState('')
  const [initialData, setInitialData] = useState({
    param: {
      debug: true
    }
  })
  const [data, setData] = useState(initialData)
  const [fieldErrors] = useState({})
  const [selectedProducts, setSelectedProducts] = useState([])
  const [outputFormat, setOutputFormat] = useState('parquet')

  useEffect(() => {
    const fetchPipelineData = async () => {
      try {
        const response = await getPipelineByName({ name: 'combine_specz' })
        const pipelineData = response.data.results[0]

        setInitialData(pipelineData)
        setData(pipelineData.system_config)
      } catch (error) {
        console.error('Error fetching pipeline data from API', error)
      }
    }
    fetchPipelineData()
  }, [])

  const handleClearForm = () => {
    setCombinedCatalogName('')
    setSelectedProducts([])
    setUniqueGalaxies(false)
    setOutputFormat('parquet')
  }

  const handleUniqueGalaxies = event => {
    setUniqueGalaxies(event.target.checked)
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
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
        'Your process has not been submitted. Please fill in the combine spec-z name.'
      )
      setSnackbarColor(theme.palette.warning.main)
      setSnackbarOpen(true)
      setIsSubmitting(false)
      return
    }

    if (selectedProducts.length < 2) {
      setSnackbarMessage('Please select at least 2 products.')
      setSnackbarColor(theme.palette.warning.main)
      setSnackbarOpen(true)
      setIsSubmitting(false)
      return
    }

    const sanitizedCatalogName = combinedCatalogName
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim()
      .replace(/[\s*,\-*/]+/g, '_')

    try {
      const pipelineId = initialData.id

      // Create the JSON object
      const processData = {
        display_name: sanitizedCatalogName,
        pipeline: pipelineId,
        used_config: {
          param: {
            debug: true,
            unique_galaxies: uniqueGalaxies
          }
        },
        description: data.param.description,
        inputs: selectedProducts.map(product => product.id),
        output_format: outputFormat
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

  const handleProductSelection = selectedProducts => {
    setSelectedProducts(selectedProducts)
  }

  const handleOutputFormatChange = event => {
    setOutputFormat(event.target.value)
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
            </Typography>
            <Typography variant="p" mb={3} textAlign={'left'}>
              The Combine Spec-z Catalogs pipeline creates a single spec-z
              sample by concatenating multiple pre-registered individual Spec-z
              Catalogs. It uses LSDB to perform spatial cross-matching
              (all-to-all) in order to identify multiple measurements of the
              same galaxies and optionally select a sample containing only
              unique objects.
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
                title="the product name of the spec-z catalog that will result from the process and be automatically registered as a new product on the PZ Server."
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
                <SpeczData
                  query={search}
                  filters={filters}
                  onSelectionChange={handleProductSelection}
                  clearSelection={selectedProducts.length === 0}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1" sx={{ color: '#888' }}>
              4. Select unique galaxies
              <Checkbox
                checked={uniqueGalaxies}
                onChange={handleUniqueGalaxies}
                inputProps={{ 'aria-label': 'controlled' }}
                disabled
              />
              <Typography component="span">(soon)</Typography>
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              5. Output format:
              <Select value={outputFormat} onChange={handleOutputFormatChange}>
                <MenuItem value="parquet">parquet</MenuItem>
                <MenuItem value="csv">csv</MenuItem>
                <MenuItem value="fits">fits</MenuItem>
                <MenuItem value="hdf5">hdf5</MenuItem>
                <MenuItem value="votable" disabled>
                  VOTable
                </MenuItem>
              </Select>
            </Typography>
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

export default SpeczCatalogs
