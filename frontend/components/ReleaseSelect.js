import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import Select from '@mui/material/Select'
import { getReleases } from '../services/product'

// export default function ReleaseSelect({ value, onChange, disabled }) {
export default function ReleaseSelect(props) {
  const { value, allowAll, onChange, disabled, ...rest } = props
  const [releases, setReleases] = useState([])

  useEffect(() => {
    getReleases().then(res => {
      return setReleases(res.results)
    })
  }, [])

  // React.useEffect(() => {
  //   // Seleciona o primeiro release
  //   // ATENÇÃO: Esta implementação não é a mais adequada.
  //   // Deveria ser implementada com UseCallback, mas eu não consegui.
  //   // executar a onChange desta forma.
  //   // a solução foi a condição value === '' que impede um loop infinito.
  //   if (releases.length > 0 && value === '') {
  //     onChange(releases[0].id)
  //   }
  // }, [onChange, releases, value])

  return (
    <Select
      id="release-select-helper"
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
      {releases.map(row => (
        <MenuItem key={row.id} value={row.id}>
          {row.display_name}
        </MenuItem>
      ))}
    </Select>
  )
}

ReleaseSelect.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  allowAll: PropTypes.bool
}
ReleaseSelect.defaultProps = {
  disabled: false,
  allowAll: false
}
