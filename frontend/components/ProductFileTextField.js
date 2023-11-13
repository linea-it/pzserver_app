import CloseIcon from '@mui/icons-material/Close'
import FormGroup from '@mui/material/FormGroup'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import TextField from '@mui/material/TextField'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'
import React from 'react'
import { deleteProductFile } from '../services/product'

export default function ProductFileTextField(props) {
  const { id, role, name, size, readOnly, onDelete } = props

  const handleRemoveFile = () => {
    deleteProductFile(id)
      .then(() => {
        // Forcar um reload dos arquivos
        onDelete(id)
      })
      .catch(res => {
        if (res.response.status === 500) {
          // TODO: Tratamento erro no backend
        }
      })
  }

  const getLabelByRole = role => {
    let label = ''
    switch (role) {
      case 0:
        label = 'Main File'
        break
      case 1:
        label = 'Description File'
        break
      case 2:
        label = 'Auxiliary File'
        break
    }
    return label
  }

  return (
    <FormGroup row key={`display_file_${id}`}>
      <TextField
        value={name}
        label={getLabelByRole(role)}
        readOnly={true}
        fullWidth
        InputProps={
          readOnly === false
            ? {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={handleRemoveFile}
                      // onMouseDown={handleMouseDownPassword}
                      edge="end"
                    >
                      <CloseIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }
            : {}
        }
        helperText={prettyBytes(Number(size))}
      />
    </FormGroup>
  )
}
ProductFileTextField.propTypes = {
  id: PropTypes.number.isRequired,
  name: PropTypes.string.isRequired,
  size: PropTypes.number.isRequired,
  role: PropTypes.number.isRequired,
  onDelete: PropTypes.func.isRequired,
  readOnly: PropTypes.bool
}
ProductFileTextField.defaultProps = {
  readOnly: false
}
