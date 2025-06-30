import {
  Alert,
  Box,
  Button,
  Checkbox,
  Container,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  Snackbar,
  TextField,
  Typography
} from '@mui/material'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import React from 'react'
import FileUploader from '../components/FileUploader'
import Loading from '../components/Loading'
import ProductTypeSelect from '../components/ProductTypeSelect'
import ReleaseSelect from '../components/ReleaseSelect'
import { createProduct } from '../services/product'
import useStyles from '../styles/pages/upload'

export default function Upload() {
  const classes = useStyles()
  const router = useRouter()

  const defaultProductValues = {
    display_name: '',
    release: '',
    product_type: '',
    official_product: false,
    main_file: null,
    description_file: '',
    survey: '',
    pz_code: '',
    description: ''
  }

  const [product, setProduct] = React.useState(defaultProductValues)
  const [isLoading, setLoading] = React.useState(false)
  const [errorSnackbar, setErrorSnackbar] = React.useState({
    open: false,
    message: ''
  })

  const onUploadProgress = e => {
    const a = Math.round((100 * e.loaded) / e.total)
    console.log('onUploadProgress: %o', a)
  }

  const handleReset = () => {
    setProduct(defaultProductValues)
  }

  const handleSubmit = e => {
    e.preventDefault()
    setLoading(true)

    createProduct(product, onUploadProgress)
      .then(res => {
        if (res.status === 201) {
          setLoading(false)
          const data = res.data
          router.push(`/product/${encodeURIComponent(data.internal_name)}`)
        }
      })
      .catch(res => {
        console.log('Error!')
        console.log(res.response.data)
        setLoading(false)
        handleOpenErrorSnackbar('Error creating the product. Please try again.')
      })
  }

  const handleOpenErrorSnackbar = message => {
    setErrorSnackbar({
      open: true,
      message
    })
  }

  const handleCloseErrorSnackbar = () => {
    setErrorSnackbar({
      open: false,
      message: ''
    })
  }

  return (
    <Container className={classes.container}>
      {isLoading && <Loading isLoading={isLoading} />}
      <Box className={classes.pageHeader}>
        <Typography variant="h6">Upload Product</Typography>
      </Box>
      <Grid container spacing={2} className={classes.gridContainer}>
        <Grid item xs={12}>
          <Box
            component="form"
            sx={{
              '& > :not(style)': { m: 1 }
            }}
            autoComplete="off"
            onSubmit={handleSubmit}
          >
            <FormControl fullWidth>
              <TextField
                id="display_name"
                name="display_name"
                value={product.display_name}
                label="Product Name"
                required
                onChange={e => {
                  setProduct({
                    ...product,
                    display_name: e.target.value
                  })
                }}
              />
            </FormControl>
            <FormControl fullWidth>
              <ProductTypeSelect
                value={product.product_type}
                onChange={value => {
                  setProduct({
                    ...product,
                    product_type: value
                  })
                }}
                required
              />
            </FormControl>
            <FormControl fullWidth>
              <ReleaseSelect
                value={product.release}
                onChange={value => {
                  setProduct({
                    ...product,
                    release: value
                  })
                }}
              />
            </FormControl>
            {/* Survey necessário Product Type = 2 - Redshift Catalog */}
            {product.product_type === 2 && (
              <FormControl fullWidth>
                <TextField
                  id="survey"
                  name="survey"
                  value={product.survey}
                  label="Survey"
                  onChange={e => {
                    setProduct({
                      ...product,
                      survey: e.target.value
                    })
                  }}
                />
              </FormControl>
            )}
            {/* Survey necessário Product Type = 1 - Photo-z Results */}
            {product.product_type === 1 && (
              <FormControl fullWidth>
                <TextField
                  id="pz_code"
                  name="pz_code"
                  value={product.pz_code}
                  label="Pz Code"
                  onChange={e => {
                    setProduct({
                      ...product,
                      pz_code: e.target.value
                    })
                  }}
                />
              </FormControl>
            )}
            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Checkbox
                    name="official_product"
                    checked={product.official_product}
                    onChange={e => {
                      setProduct({
                        ...product,
                        official_product: e.target.checked
                      })
                    }}
                  />
                }
                label="Official Product"
              />
            </FormControl>

            <FormGroup row>
              <TextField
                name="main_file"
                value={product.main_file ? product.main_file.name : ''}
                label="Main File"
                readOnly
                required
              />
              <FileUploader
                id="main_file"
                onFileSelectSuccess={file => {
                  setProduct({
                    ...product,
                    main_file: file
                  })
                }}
                onFileSelectError={e => {
                  console.log(e)
                }}
                maxSize={200} // 200 MB
              />
            </FormGroup>
            <FormControl fullWidth>
              <TextField
                id="description"
                name="description"
                value={product.description}
                label="Description"
                multiline
                minRows={8}
                onChange={e => {
                  setProduct({
                    ...product,
                    description: e.target.value
                  })
                }}
                required
              />
            </FormControl>

            <Grid item xs={12} className={classes.buttonsContainer}>
              <Button
                type="reset"
                value="reset"
                variant="contained"
                color="secondary"
                onClick={handleReset}
              >
                Clear Form
              </Button>
              <Button type="submit" variant="contained" color="primary">
                Submit
              </Button>
            </Grid>
            <Snackbar
              open={errorSnackbar.open}
              autoHideDuration={6000}
              onClose={handleCloseErrorSnackbar}
            >
              <Alert
                onClose={handleCloseErrorSnackbar}
                severity="error"
                sx={{ width: '100%' }}
              >
                {errorSnackbar.message}
              </Alert>
            </Snackbar>
          </Box>
        </Grid>
      </Grid>
    </Container>
  )
}

export const getServerSideProps = async ctx => {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (!token) {
    return {
      redirect: {
        destination: '/login',
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
}
