import React, { useState, useEffect } from 'react'
import TextField from '@mui/material/TextField'
import PropTypes from 'prop-types'

const SearchRadius = ({ searchRadius, onChange, reset }) => {
  const formatSearchRadius = value => {
    if (/^\d+\.\d*$/.test(value)) {
      return value
    } else {
      return value.replace(/[^\d.]/g, '')
    }
  }

  const [localSearchRadius, setLocalSearchRadius] = useState(
    formatSearchRadius(searchRadius)
  )

  useEffect(() => {
    setLocalSearchRadius(formatSearchRadius(searchRadius))
  }, [reset, searchRadius])

  const handleRadiusChange = event => {
    const inputValue = event.target.value

    if (/^\d+(\.\d*)?$/.test(inputValue)) {
      setLocalSearchRadius(inputValue)
      onChange(event)
    }
  }

  return (
    <TextField
      id="searchRadius"
      variant="outlined"
      value={localSearchRadius}
      onChange={handleRadiusChange}
    />
  )
}

SearchRadius.propTypes = {
  searchRadius: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onChange: PropTypes.func,
  reset: PropTypes.bool
}

export default SearchRadius
