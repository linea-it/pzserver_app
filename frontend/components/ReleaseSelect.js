import React, { useState, useEffect } from 'react'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import Select from '@mui/material/Select'
import { getReleases } from '../services/product'

export default function ReleaseSelect() {
  const [Releases, setReleases] = useState([])

  const [release, setRelease] = React.useState('')

  useEffect(() => {
    getReleases().then(res => {
      return setReleases(res.results)
    })
  }, [])

  const handleChange = event => {
    setRelease(event.target.value)
  }

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 200 }}>
        <InputLabel id="release-select-label">Release</InputLabel>
        <Select
          labelId="release-select-label"
          id="release-select-helper"
          value={release}
          label="Release"
          onChange={handleChange}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {Releases.map(row => (
            <MenuItem key={row.id} value={row.id}>
              {row.display_name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  )
}
