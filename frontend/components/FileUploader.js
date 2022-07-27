import React from 'react'
import { Input, Button } from '@mui/material'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'

export default function FileUploader(props) {
  const { id, onFileSelectSuccess, onFileSelectError, maxSize, buttonProps, ...rest } = props
  // const fileInput = useRef(null)

  const handleFileInput = e => {
    // Converte o valor passado no props para MB.
    const mSize = parseInt(maxSize) * 1000000

    // handle validations
    const file = e.target.files[0]
    if (file) {
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
      <Button
        variant="contained"
        component="span"
        size="large"
        // disableElevation
        sx={{ height: '100%' }}
        {...buttonProps}
      >
        {buttonProps && buttonProps.label ? buttonProps.label : 'Choose File'}
      </Button>
    </label>
  )
}
FileUploader.propTypes = {
  id: PropTypes.string.isRequired,
  onFileSelectSuccess: PropTypes.func.isRequired,
  onFileSelectError: PropTypes.func.isRequired,
  maxSize: PropTypes.number
}
FileUploader.defaultProps = {
  maxSize: 50
}
