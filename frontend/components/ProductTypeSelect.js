import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import MenuItem from '@mui/material/MenuItem'
import { getProductTypes } from '../services/product'
import { TextField } from '@mui/material'
export default function ProductTypeSelect(props) {
  const { allowAll, value, onChange, disabled, useId, ...rest } = props

  const [rows, setRows] = useState([])

  useEffect(() => {
    getProductTypes().then(res => {
      return setRows(res.results)
    })
  }, [])

  const handleChange = id => {
    if (useId === true) {
      onChange(id)
    }
    if (useId === false) {
      const record = rows.find(x => x.id === id)
      onChange(record)
    }
  }

  return (
    <TextField
      select
      value={rows.length > 0 ? value : ''}
      label="Product Type"
      onChange={e => handleChange(e.target.value)}
      defaultValue=""
      disabled={disabled}
      {...rest}
    >
      {allowAll === true && (
        <MenuItem value="">
          <em>All</em>
        </MenuItem>
      )}
      {rows.map(row => (
        <MenuItem key={row.id} value={row.id}>
          {row.display_name}
        </MenuItem>
      ))}
    </TextField>
  )
}

ProductTypeSelect.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  allowAll: PropTypes.bool,
  useId: PropTypes.bool
}
ProductTypeSelect.defaultProps = {
  disabled: false,
  allowAll: false,
  useId: true
}
