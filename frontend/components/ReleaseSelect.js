import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import MenuItem from '@mui/material/MenuItem'
import { getReleases } from '../services/product'
import { TextField } from '@mui/material'

// export default function ReleaseSelect({ value, onChange, disabled }) {
export default function ReleaseSelect(props) {
  const { value, allowAll, noRelease, onChange, disabled, ...rest } = props
  const [releases, setReleases] = useState([])

  useEffect(() => {
    getReleases().then(res => {
      return setReleases(res.results)
    })
  }, [])

  return (
    // <Select
    <TextField
      select
      value={value}
      label="Release"
      onChange={e => onChange(e.target.value)}
      defaultValue=""
      disabled={disabled}
      {...rest}
    >
      {allowAll === true && (
        <MenuItem value="">
          <em>All</em>
        </MenuItem>
      )}

      {noRelease === true && (
        <MenuItem value="0">
          <em>None</em>
        </MenuItem>
      )}

      {releases.map(row => (
        <MenuItem key={row.id} value={row.id}>
          {row.display_name}
        </MenuItem>
      ))}
      {/* </Select> */}
    </TextField>
  )
}

ReleaseSelect.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  noRelease: PropTypes.bool,
  allowAll: PropTypes.bool
}
ReleaseSelect.defaultProps = {
  disabled: false,
  noRelease: false,
  allowAll: false
}
