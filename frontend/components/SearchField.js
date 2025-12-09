import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash/debounce'
import FormControl from '@mui/material/FormControl'
import TextField from '@mui/material/TextField'
import InputAdornment from '@mui/material/InputAdornment'
import SearchIcon from '@mui/icons-material/Search'

export default function SearchField({ initialValue, onChange }) {
  const [inputValue, setInputValue] = useState(initialValue || '')

  const sendQuery = query => {
    onChange(query)
  }

  // Using lodash debounce to Delay search by 600ms
  // Exemplo: https://www.upbeatcode.com/react/how-to-use-lodash-in-react/
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const delayedSearch = useCallback(
    debounce(q => sendQuery(q), 600),
    []
  )

  const handleChange = event => {
    // Input will be changed immidiately
    setInputValue(event.target.value)

    // Search will only be called when user stops typing
    delayedSearch(event.target.value)
  }

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 400 }}>
        <TextField
          label="Search"
          value={inputValue}
          onChange={handleChange}
          type="search"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <SearchIcon />
              </InputAdornment>
            )
          }}
        />
      </FormControl>
    </div>
  )
}

SearchField.propTypes = {
  initialValue: PropTypes.string,
  onChange: PropTypes.func.isRequired
}
