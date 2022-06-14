import React, { useRef } from 'react'
import { Input, Button } from '@mui/material'
import prettyBytes from 'pretty-bytes'

export default function FileUploader(props) {
  const { id, onFileSelectSuccess, onFileSelectError, maxSize, ...rest } = props
  // const fileInput = useRef(null)

  const handleFileInput = e => {
    // Converte o valor passado no props para MB.
    const mSize = parseInt(maxSize) * 1000000

    // handle validations
    const file = e.target.files[0]

    if (file.size > mSize) {
      onFileSelectError({
        error: `File size cannot exceed more than ${prettyBytes(
          parseInt(mSize)
        )}`
      })
    } else {
      onFileSelectSuccess(file)
    }
  }

  return (
    <label htmlFor={id}>
      <Input
        id={id}
        // accept="image/*"
        type="file"
        sx={{ display: 'none' }}
        onChange={handleFileInput}
        {...rest}
      />
      <Button variant="contained" component="span" disableElevation>
        Upload
      </Button>
    </label>
  )
}
