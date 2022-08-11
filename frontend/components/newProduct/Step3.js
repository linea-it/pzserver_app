import React, { useState, useEffect } from 'react'
import {
  TextField,
  FormControl,
  Button,
  Box,
  Stack,
  Alert
} from '@mui/material'
import MenuItem from '@mui/material/MenuItem'
import Loading from '../Loading'
import InputAdornment from '@mui/material/InputAdornment'
import CloseIcon from '@mui/icons-material/Close'
import IconButton from '@mui/material/IconButton'
import { getProductContents, contentAssociation } from '../../services/product'
import PropTypes from 'prop-types'

export default function NewProductStep3({ productId, onNext, onPrev }) {
  const ucds = [
    {
      name: 'ID',
      value: 'meta.id;meta.main'
    },
    {
      name: 'RA',
      value: 'pos.eq.ra;meta.main'
    },
    {
      name: 'Dec',
      value: 'pos.eq.dec;meta.main'
    }
  ]

  const [productColumns, setProductColumns] = React.useState([])
  const [usedUcds, setUsedUcds] = React.useState([])
  const [isLoading, setLoading] = useState(false)
  const [formError, setFormError] = React.useState('')

  const loadContents = React.useCallback(async () => {
    setLoading(true)
    getProductContents(productId)
      .then(res => {
        setProductColumns(res.results)

        setLoading(false)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }, [productId])

  useEffect(() => {
    loadContents()
  }, [loadContents])

  useEffect(() => {
    const useducds = []
    productColumns.forEach(row => {
      if (row.ucd !== null) {
        useducds.push(row.ucd)
      }
    })
    setUsedUcds(useducds)
  }, [productColumns])

  const handleSubmit = () => {
    onNext(productId)
  }
  const handlePrev = () => {
    onPrev(productId)
  }
  const onChangeUcd = (pc, value) => {
    if (pc.ucd === value) {
      return
    }

    // setLoading(true)
    contentAssociation(pc.id, value)
      .then(() => {
        // setLoading(false)
        loadContents(productId)
      })
      .catch(res => {
        setLoading(false)

        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }
  const handleMouseDownPassword = event => {
    event.preventDefault()
  }
  const createSelect = pc => {
    // Check Available Ucds and Current UCD when pc.ucd is not null
    const avoptions = []
    let currentUcd = null
    ucds.forEach(ucd => {
      if (usedUcds.indexOf(ucd.value) === -1 || ucd.value === pc.ucd) {
        avoptions.push(ucd)
      }
      if (ucd.value === pc.ucd) {
        currentUcd = ucd
      }
    })

    if (pc.ucd !== null ? pc.ucd : '') {
      return (
        <TextField
          value={currentUcd.name}
          readOnly
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => onChangeUcd(pc, null)}
                  onMouseDown={handleMouseDownPassword}
                  edge="end"
                >
                  <CloseIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      )
    } else {
      return (
        <TextField
          select
          onChange={e => onChangeUcd(pc, e.target.value)}
          defaultValue=""
        >
          {avoptions.map(ucd => (
            <MenuItem key={`${pc.column_name}_${ucd.name}`} value={ucd.value}>
              {ucd.name}
            </MenuItem>
          ))}
        </TextField>
      )
    }
  }

  const createFields = pc => {
    return (
      <Stack
        direction="row"
        spacing={2}
        key={`fields_${pc.column_name}`}
        mb={2}
      >
        <FormControl>
          <TextField value={pc.column_name} />
        </FormControl>
        <FormControl>{createSelect(pc)}</FormControl>
      </Stack>
    )
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
      <Box
        component="form"
        sx={{
          '& .MuiTextField-root': { width: '25ch' }
        }}
        autoComplete="off"
      >
        {productColumns.map(pc => {
          return createFields(pc)
        })}
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
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Next
        </Button>
      </Box>
    </React.Fragment>
  )
}

NewProductStep3.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}
