import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  TextField,
  Typography
} from '@mui/material'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import dayjs from 'dayjs'
import PropTypes from 'prop-types'
import React from 'react'
import Loading from '../../components/Loading'
import ProductTypeSelect from '../../components/ProductTypeSelect'
import ReleaseSelect from '../../components/ReleaseSelect'
import { useAuth } from '../../contexts/AuthContext'
import { createProduct, getProduct, patchProduct } from '../../services/product'

export default function NewProductStep1({ productId, onNext, onDiscard }) {
  const { user } = useAuth()
  const defaultProductValues = {
    id: null,
    display_name: '',
    release: '',
    product_type: '',
    official_product: false,
    survey: '',
    pz_code: '',
    description: '',
    release_year: '',
    status: 0
  }
  const [product, setProduct] = React.useState(defaultProductValues)
  const [prodType, setProdType] = React.useState(null)
  const [isLoading, setLoading] = React.useState(false)
  const [fieldErrors, setFieldErrors] = React.useState({})
  const [formError, setFormError] = React.useState('')

  const loadProduct = React.useCallback(async () => {
    if (productId && productId !== product.id) {
      setLoading(true)
      getProduct(productId)
        .then(res => {
          setLoading(false)
          setProduct(res)
        })
        .catch(res => {
          setLoading(false)
        })
    }
  }, [product, productId])

  React.useEffect(() => {
    loadProduct()
  }, [loadProduct, productId])

  const handleInputValue = e => {
    const { name, value } = e.target

    setProduct({
      ...product,
      [name]: value
    })

    setFieldErrors({
      ...fieldErrors,
      [name]: ''
    })
  }

  const handleProductTypeValue = e => {
    const value = e

    setProduct({
      ...product,
      product_type: value,
      release: '',
      release_year: '',
      pz_code: ''
    })

    setFieldErrors({
      ...fieldErrors,
      product_type: ''
    })
  }

  const handleSubmit = () => {
    // Ao submeter limpa os errors
    setFieldErrors({})
    setFormError('')

    if (product.id === null) {
      createProduct(product)
        .then(res => {
          if (res.status === 201) {
            setLoading(false)
            const data = res.data

            // Muda para o proximo step do formulário
            onNext(data.id)
          }
        })
        .catch(res => {
          if (res.response.status === 400) {
            // Tratamento para erro nos campos
            handleFieldsErrors(res.response.data)
          }
          if (res.response.status === 500) {
            // Tratamento erro no backend
            catchFormError(res.response.data)
          }
          setLoading(false)
        })
    } else {
      // Fazer update do produto
      patchProduct(product)
        .then(res => {
          if (res.status === 200) {
            setLoading(false)
            const data = res.data

            // Muda para o proximo step do formulário
            onNext(data.id)
          }
        })
        .catch(res => {
          if (res.response.status === 400) {
            // Tratamento para erro nos campos
            handleFieldsErrors(res.response.data)
          }
          if (res.response.status === 500) {
            // Tratamento erro no backend
            catchFormError(res.response.data)
          }
          setLoading(false)
        })
    }
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later, if the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  const handleFieldsErrors = data => {
    const errors = {}
    Object.keys(data).forEach((key, index) => {
      errors[key] = data[key]
    })
    setFieldErrors(errors)
  }

  const handleFormError = () => {
    return (
      <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
        {formError}
      </Alert>
    )
  }

  const handleReset = () => {
    setProduct(defaultProductValues)
  }

  if (product === null) {
    return null
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Typography paragraph variant="body">
        Please provide the basic information about the new data product.
      </Typography>
      <Box
        component="form"
        sx={{
          '& > :not(style)': { mb: 4 }
        }}
        autoComplete="off"
      >
        <FormControl fullWidth>
          <TextField
            name="display_name"
            value={product.display_name}
            label="Product Name"
            required
            error={!!fieldErrors.display_name}
            helperText={fieldErrors.display_name}
            onChange={handleInputValue}
            onBlur={handleInputValue}
          />
        </FormControl>
        <FormControl fullWidth>
          <ProductTypeSelect
            name="product_type"
            disabled={!!product.id}
            value={product.product_type}
            useId={false}
            onChange={prodType => {
              handleProductTypeValue(prodType.id)
              setProdType(prodType.name)
            }}
            required
            error={!!fieldErrors.product_type}
            helperText={fieldErrors.product_type}
          />
        </FormControl>
        {/* Release necessário Product Type != specz_catalog or objects_catalog */}
        {!['objects_catalog', 'specz_catalog', null].includes(prodType) && (
          <FormControl fullWidth>
            <ReleaseSelect
              name="release"
              value={product.release ? product.release : ''}
              onChange={value => {
                handleInputValue({ target: { name: 'release', value: value } })
              }}
              onBlur={handleInputValue}
              error={!!fieldErrors.release}
              helperText={fieldErrors.release}
            />
          </FormControl>
        )}
        {/* Release year necessário Product Type = specz_catalog - Spec-z Catalog */}
        {prodType === 'specz_catalog' && (
          <FormControl>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                name="release_year"
                views={['year']}
                label="Release year"
                value={
                  product.release_year
                    ? dayjs().set('year', product.release_year)
                    : null
                }
                onChange={newValue => {
                  handleInputValue({
                    target: {
                      name: 'release_year',
                      value: newValue.get('year')
                    }
                  })
                }}
                onBlur={handleInputValue}
                renderInput={params => (
                  <TextField
                    {...params}
                    helperText={fieldErrors.release_year}
                    error={!!fieldErrors.release_year}
                    required
                  />
                )}
                disableFuture
              />
            </LocalizationProvider>
          </FormControl>
        )}
        {/* Survey necessário Product Type = validation_results - Photo-z Results */}
        {prodType === 'validation_results' && (
          <FormControl fullWidth>
            <TextField
              name="pz_code"
              value={product.pz_code}
              label="Pz Code"
              onChange={handleInputValue}
              onBlur={handleInputValue}
              error={!!fieldErrors.pz_code}
              helperText={fieldErrors.pz_code}
            />
          </FormControl>
        )}
        {/* Survey necessário Product Type = photoz_table - Photo-z Table */}
        {prodType === 'photoz_table' && (
          <FormControl fullWidth>
            <TextField
              name="pz_code"
              value={product.pz_code}
              label="Pz Code"
              onChange={handleInputValue}
              onBlur={handleInputValue}
              error={!!fieldErrors.pz_code}
              helperText={fieldErrors.pz_code}
            />
          </FormControl>
        )}
        {user?.is_admin === true && (
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
        )}
        <FormControl fullWidth>
          <TextField
            name="description"
            value={product.description}
            label="Description"
            multiline
            minRows={6}
            onChange={handleInputValue}
            onBlur={handleInputValue}
            error={!!fieldErrors.description}
            helperText={fieldErrors.description}
          />
        </FormControl>
      </Box>
      {formError !== '' && handleFormError()}
      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleReset}
          sx={{ mr: 1 }}
          disabled={product.id !== null}
        >
          Clear Form
        </Button>
        {product.id !== null && (
          <Button
            variant="contained"
            color="secondary"
            onClick={() => onDiscard(product)}
          >
            Discard
          </Button>
        )}
        <Box sx={{ flex: '1 1 auto' }} />
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Next
        </Button>
      </Box>
    </React.Fragment>
  )
}

NewProductStep1.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onDiscard: PropTypes.func.isRequired
}
