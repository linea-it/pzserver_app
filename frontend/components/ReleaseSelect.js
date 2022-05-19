import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import Select from '@mui/material/Select'
import { getReleases } from '../services/product'

export default function ReleaseSelect({ value, onChange }) {
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
    <div>
      <FormControl sx={{ m: 1, minWidth: 200 }}>
        <InputLabel id="release-select-label">Release</InputLabel>
        <Select
          labelId="release-select-label"
          id="release-select-helper"
          value={value}
          label="Release"
          onChange={e => onChange(e.target.value)}
          // readOnly={releases.length === 1}
          defaultValue=""
        >
          <MenuItem value="">
            <em>All</em>
          </MenuItem>
          {releases.map(row => (
            <MenuItem key={row.id} value={row.id}>
              {row.display_name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  )
}

ReleaseSelect.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired
}
