import InfoIcon from '@mui/icons-material/Info'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import Link from '@mui/material/Link'
import Breadcrumbs from '@mui/material/Breadcrumbs'
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
import SpeczData from '../components/SpeczData'
import { useTheme } from '@mui/system'

function SpeczCatalogs() {
  const theme = useTheme()

  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [search, setSearch] = React.useState('')
  const filters = React.useState()
  const [searchRadius, setSearchRadius] = useState('1.0')
  const [selectedOption, setSelectedOption] = useState('keepAll')
  const [email, setEmail] = useState('')
  const [snackbarOpen, setSnackbarOpen] = useState(false)

  const handleCatalogNameChange = event => {
    setCombinedCatalogName(event.target.value)
  }

  const handleSearchRadiusChange = event => {
    const newValue = parseFloat(event.target.value)
    setSearchRadius(isNaN(newValue) ? '' : newValue.toString())
  }

  const handleEmailChange = newEmail => {
    setEmail(newEmail)
  }

  const handleClearForm = () => {
    setCombinedCatalogName('')
    setSearchRadius('1.0')
    setSelectedOption('keepAll')
    setEmail('')
  }

  const handleRun = () => {
    setSnackbarOpen(true)
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
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
            <Box display="flex" alignItems="center">
              <Typography variant="body1" mb={1}>
                2. Select the Spec-z Catalogs to include in your sample:
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
            <Typography variant="body1" mb={'12px'}>
              3. Select the cross-matching configuration choices:
            </Typography>
          </Grid>

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
            >
              <MenuItem value="keepAll">Keep all</MenuItem>
              <MenuItem value="pickOne">
                Pick the one with (1) the highest confidence flag; (2) the
                smallest redshift error; (3) the latest upload to PZ Server.
              </MenuItem>
              <MenuItem value="computeMean">Compute mean redshift</MenuItem>
            </Select>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body1">
              4. Enter an email address to be notified when the process is
              complete (opcional):
            </Typography>
            <EmailField
              initialValue={email}
              onEmailChange={handleEmailChange}
              onClearForm={handleClearForm}
            />
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
