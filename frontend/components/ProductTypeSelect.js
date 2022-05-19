import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import Select from '@mui/material/Select'
import { getProductTypes } from '../services/product'

export default function ProductTypeSelect({ value, onChange, disabled }) {
  const [rows, setRows] = useState([])

  useEffect(() => {
    getProductTypes().then(res => {
      return setRows(res.results)
    })
  }, [])

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 200 }}>
        <InputLabel id="producttype-select-label">Product Type</InputLabel>
        <Select
          labelId="producttype-select-label"
          id="producttype-select-helper"
          value={value}
          label="Product Type"
          onChange={e => onChange(e.target.value)}
          defaultValue=""
          disabled={disabled}
        >
          <MenuItem value="">
            <em>All</em>
          </MenuItem>
          {rows.map(row => (
            <MenuItem key={row.id} value={row.id}>
              {row.display_name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  )
}

ProductTypeSelect.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}
ProductTypeSelect.defaultProps = {
  disabled: false
}
