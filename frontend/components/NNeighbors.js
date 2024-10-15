import React, { useState, useEffect } from 'react'
import TextField from '@mui/material/TextField'
import PropTypes from 'prop-types'

const NNeighbors = ({ nNeighbors, onChange }) => {
  const [localNNeighbors, setLocalNNeighbors] = useState(nNeighbors)

  useEffect(() => {
    setLocalNNeighbors(nNeighbors)
  }, [nNeighbors])

  const handleNeighborsChange = event => {
    const inputValue = event.target.value.replace(/[^\d]/g, '')
    const newValue = parseInt(inputValue, 10) || 1
    setLocalNNeighbors(newValue)
    onChange(newValue)
  }

  return (
    <TextField
      id="nNeighbors"
      variant="outlined"
      value={localNNeighbors}
      onChange={handleNeighborsChange}
      inputProps={{ inputMode: 'numeric', pattern: '[0-9]*', min: 1, step: 1 }}
    />
  )
}

NNeighbors.propTypes = {
  nNeighbors: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    .isRequired,
  onChange: PropTypes.func.isRequired
}

export default NNeighbors
