import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import FormControl from '@mui/material/FormControl'
import TextField from '@mui/material/TextField'
import InputAdornment from '@mui/material/InputAdornment'
import IconButton from '@mui/material/IconButton'
import SearchIcon from '@mui/icons-material/Search'
// TODO: Utilizar lodash debounce para que a busca só aconteça quando o usuario parar de digitar.
// https://www.upbeatcode.com/react/how-to-use-lodash-in-react/
export default function SearchField({ value, onChange }) {

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 400 }}>
        <TextField
          label="Search"
          value={value}
          onChange={onChange}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton>
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </FormControl>
    </div>
  )
}

SearchField.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired
}
