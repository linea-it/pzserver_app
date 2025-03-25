import React, { useEffect, useRef, useState } from 'react'
import { Button, Box, Alert, Typography } from '@mui/material'
import Loading from '../../components/Loading'
import ProductDetail from '../ProductDetail'
import { changeProductStatus } from '../../services/product'
import PropTypes from 'prop-types'

export default function NewProductStep4({ productId, onNext, onPrev }) {
  const [isLoading, setLoading] = React.useState(false)
  const [formError, setFormError] = React.useState('')

  const finishButtonRef = useRef(null)
  const [highlight, setHighlight] = useState(false)

  useEffect(() => {
    // Pequeno atraso para garantir que o DOM esteja atualizado antes de rolar
    const timeout = setTimeout(() => {
      if (finishButtonRef.current) {
        finishButtonRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
        setHighlight(true)
        setTimeout(() => setHighlight(false), 1500)
      }
    }, 300)

    return () => clearTimeout(timeout)
  }, [])

  const handleSubmit = () => {
    setLoading(true)

    changeProductStatus(productId, 1)
      .then(res => {
        if (res.status === 200) {
          setLoading(false)
          onNext(res.data.internal_name)
        }
      })
      .catch(error => {
        setLoading(false)
        if (error.response) {
          catchFormError(error.response.data)
        } else {
          console.error('Ocorreu um erro:', error)
        }
      })
  }

  const handlePrev = () => {
    onPrev(productId)
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later. If the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Typography paragraph variant="body">
        Please review your information before pressing the FINISH button.
      </Typography>
      <Box>
        <Box>
          <ProductDetail productId={productId} />
        </Box>
        {formError && (
          <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
            {formError}
          </Alert>
        )}
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
          <Button
            variant="contained"
            color="success"
            onClick={handleSubmit}
            ref={finishButtonRef}
            sx={{
              animation: highlight ? 'blink 0.5s ease-in-out 3' : 'none'
            }}
          >
            Finish
          </Button>
        </Box>
      </Box>
      <style>
        {`
          @keyframes blink {
            0% { background-color: #4caf50; }
            25% { background-color: #81c784; }
            50% { background-color: #81c784; }
            100% { background-color: #4caf50; }
          }
        `}
      </style>
    </React.Fragment>
  )
}

NewProductStep4.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}
