import CloseIcon from '@mui/icons-material/Close'
import FormGroup from '@mui/material/FormGroup'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import TextField from '@mui/material/TextField'
import Snackbar from '@mui/material/Snackbar'
import MuiAlert from '@mui/material/Alert'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'
import React from 'react'
import { deleteProductFile } from '../services/product'

export default function ProductFileTextField(props) {
  const { id, role, name, size, readOnly, onDelete } = props

  const [errorSnackbar, setErrorSnackbar] = React.useState({
    open: false,
    message: ''
  })

  const handleOpenErrorSnackbar = message => {
    setErrorSnackbar({
      open: true,
      message
    })
  }

  const handleRemoveFile = () => {
    deleteProductFile(id)
      .then(() => {
        // Forcar um reload dos arquivos
        onDelete(id)
      })
      .catch(res => {
        if (res.response.status === 500) {
          handleOpenErrorSnackbar('Server error. Please try again later.')
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
    <React.Fragment>
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
      <Snackbar
        open={errorSnackbar.open}
        autoHideDuration={6000}
        onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
      >
        <MuiAlert
          elevation={6}
          variant="filled"
          severity="error"
          onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
        >
          {errorSnackbar.message}
        </MuiAlert>
      </Snackbar>
    </React.Fragment>
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
