import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  TextField
} from '@mui/material'
import DialogActions from '@mui/material/DialogActions'
import InputAdornment from '@mui/material/InputAdornment'

import PropTypes from 'prop-types'
import React from 'react'

export default function ProductShare({
  isOpen,
  handleShareDialogOpen,
  url,
  setParentSnackbarOpen
}) {
  const handleCopyUrl = () => {
    navigator.clipboard
      .writeText(url)
      .then(() => {
        handleShareDialogOpen()
        setParentSnackbarOpen(true)
      })
      .catch(error => {
        console.error(error)
      })
  }

  return (
    <Dialog
      open={isOpen}
      onClose={handleShareDialogOpen}
      PaperProps={{
        style: { width: '500px', minHeight: '150px' }
      }}
    >
      <DialogTitle style={{ fontSize: '16px' }}>
        Copy the download URL:
      </DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          variant="outlined"
          value={url}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <Button variant="contained" onClick={handleCopyUrl}>
                  Copy
                </Button>
              </InputAdornment>
            )
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleShareDialogOpen}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

ProductShare.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  handleShareDialogOpen: PropTypes.func.isRequired,
  url: PropTypes.string,
  setParentSnackbarOpen: PropTypes.func.isRequired
}
