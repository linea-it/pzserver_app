import React from 'react'
import PropTypes from 'prop-types'
import TextField from '@mui/material/TextField'

function SearchRadius({ searchRadius, onChange }) {
  const formattedRadius = searchRadius.toFixed(1)

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
