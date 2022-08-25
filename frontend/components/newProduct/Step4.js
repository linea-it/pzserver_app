import React from 'react'
import { Button, Box, Alert } from '@mui/material'
import Loading from '../../components/Loading'
import ProductDetail from '../ProductDetail'
import { changeProductStatus } from '../../services/product'
import PropTypes from 'prop-types'
export default function NewProductStep4({ productId, onNext, onPrev }) {
  const [isLoading, setLoading] = React.useState(false)
  const [formError, setFormError] = React.useState('')

  const handleSubmit = e => {
    // Altera o status do produto para 1 = Published
    setLoading(true)

    changeProductStatus(productId, 1)
      .then(res => {
        if (res.status === 200) {
          setLoading(false)
          const data = res.data
          onNext(data.internal_name)
        }
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 400) {
          // Tratamento para erro nos campos
          catchFormError(res.response.data)
        }
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }
  const handlePrev = () => {
    onPrev(productId)
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later, if the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  const handleFormError = () => {
    return (
      <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
        {formError}
      </Alert>
    )
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Box>
        <Box>
          <ProductDetail productId={productId}></ProductDetail>
        </Box>
        {formError !== '' && handleFormError()}
        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            variant="contained"
            color="secondary"
            onClick={handlePrev}
            sx={{ mr: 1 }}
          >
            Prev
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          <Button variant="contained" color="success" onClick={handleSubmit}>
            Finish
          </Button>
        </Box>
      </Box>
    </React.Fragment>
  )
}

NewProductStep4.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}