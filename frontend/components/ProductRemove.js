import React from 'react'
import PropTypes from 'prop-types'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import Button from '@mui/material/Button'
import LoadingButton from '@mui/lab/LoadingButton'
import { deleteProduct } from '../services/product'
export default function ProductRemove({
  recordId,
  productName,
  onRemoveSuccess,
  onClose,
  onError
}) {
  const [isLoading, setLoading] = React.useState(false)
  const [errorDialogOpen, setErrorDialogOpen] = React.useState(false)

  const handleDelete = () => {
    setLoading(true)
    deleteProduct(recordId)
      .then(() => {
        onRemoveSuccess()
        onClose()
      })
      .catch(error => {
        setLoading(false)
        if (error.response && error.response.status < 500) {
          onError(
            'Failed to remove the product. Please check your input and try again.'
          )
        } else {
          setErrorDialogOpen(true)
        }
      })
  }

  if (recordId === null) return null

  return (
    <>
      <Dialog open={true}>
        <DialogTitle>{'Delete this Product?'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {`Are you sure you want to delete the product "${productName}"?`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <LoadingButton
            loading={isLoading}
            variant="contained"
            onClick={handleDelete}
          >
            Delete
          </LoadingButton>
        </DialogActions>
      </Dialog>
      <Dialog open={errorDialogOpen} onClose={() => setErrorDialogOpen(false)}>
        <DialogTitle>Error</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Failed to remove the product. Please try again later or contact the
            helpdesk at helpdesk@linea.org.br.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setErrorDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

ProductRemove.propTypes = {
  recordId: PropTypes.number,
  productName: PropTypes.string,
  onRemoveSuccess: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired
}
