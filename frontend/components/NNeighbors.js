import React, { useState, useEffect } from 'react'
import TextField from '@mui/material/TextField'
import PropTypes from 'prop-types'

const NNeighbors = ({ nNeighbors, onChange, reset }) => {
  const formatNNeighbors = value => {
    if (/^\d*\.?\d*$/.test(value)) {
      return value
    } else {
      return value.replace(/[^\d.]/g, '')
    }
  }

  const [localNNeighbors, setLocalNNeighbors] = useState(
    formatNNeighbors(nNeighbors)
  )

  useEffect(() => {
    setLocalNNeighbors(formatNNeighbors(nNeighbors))
  }, [reset, nNeighbors])

  const handleNeighborsChange = event => {
    const inputValue = formatNNeighbors(event.target.value)
    const newValue = Math.min(parseFloat(inputValue) || 0, 90)
    setLocalNNeighbors(inputValue)
    onChange(newValue)
  }

  return (
    <TextField
      id="nNeighbors"
      variant="outlined"
      value={localNNeighbors}
      onChange={handleNeighborsChange}
      inputProps={{ inputMode: 'decimal', pattern: '[0-9]*\\.?[0-9]*' }}
    />
  )
}

NNeighbors.propTypes = {
  nNeighbors: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onChange: PropTypes.func.isRequired,
  reset: PropTypes.bool
}

export default NNeighbors
