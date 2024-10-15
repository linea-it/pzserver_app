import TextField from '@mui/material/TextField'
import PropTypes from 'prop-types'
import React from 'react'

function SearchRadius({ searchRadius, onChange }) {
  const formattedRadius = searchRadius.toLocaleString('en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  })

  const handleRadiusChange = event => {
    onChange(parseFloat(event.target.value))
  }

  return (
    <TextField
      type="number"
      value={formattedRadius}
      onChange={handleRadiusChange}
      inputProps={{ min: 0, max: 90, step: 0.1 }}
    />
  )
}

SearchRadius.propTypes = {
  searchRadius: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired
}

export default SearchRadius
