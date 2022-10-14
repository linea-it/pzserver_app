import React from 'react'
import {
  TextField,
  Checkbox,
  FormControl,
  FormControlLabel,
  Button,
  Box,
  Typography,
  Alert
} from '@mui/material'
import ProductTypeSelect from '../../components/ProductTypeSelect'
import ReleaseSelect from '../../components/ReleaseSelect'
import { getProduct, createProduct, patchProduct } from '../../services/product'
import Loading from '../../components/Loading'
import PropTypes from 'prop-types'
import { useAuth } from '../../contexts/AuthContext'
export default function NewProductStep1({ productId, onNext }) {
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
    status: 0
  }
  const [product, setProduct] = React.useState(defaultProductValues)
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
      errors[key] = data[key].join(' ')
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
            value={product.product_type}
            onChange={value => {
              handleInputValue({
                target: { name: 'product_type', value: value }
              })
            }}
            onBlur={handleInputValue}
            required
            error={!!fieldErrors.product_type}
            helperText={fieldErrors.product_type}
          />
        </FormControl>
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
        {/* Survey necessário Product Type = 2 - Spec-z Catalog */}
        {product.product_type === 2 && (
          <FormControl fullWidth>
            <TextField
              name="survey"
              value={product.survey}
              label="Survey"
              onChange={handleInputValue}
              onBlur={handleInputValue}
              error={!!fieldErrors.survey}
              helperText={fieldErrors.survey}
            />
          </FormControl>
        )}
        {/* Survey necessário Product Type = 1 - Photo-z Results */}
        {product.product_type === 1 && (
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
  onNext: PropTypes.func.isRequired
}
