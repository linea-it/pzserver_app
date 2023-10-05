import LoadingButton from '@mui/lab/LoadingButton'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import PropTypes from 'prop-types'
import React from 'react'
import { deleteProduct } from '../services/product'

export default function ProductRemove({
  recordId,
  onRemoveSuccess,
  onClose,
  onError
}) {
  const [isLoading, setLoading] = React.useState(false)
  const [isAuthorized, setAuthorized] = React.useState(true)

  const handleDelete = async () => {
    setLoading(true)
    try {
      await deleteProduct(recordId)
      onRemoveSuccess()
      onClose()
    } catch (error) {
      if (error.response && error.response.status === 403) {
        setAuthorized(false)
      } else {
        onError(
          'Failed to remove the product. Please try again later or contact the helpdesk.'
        )
      }
      setLoading(false)
    }
  }

  if (recordId === null) return null

  return (
    <Dialog open={true}>
      <DialogTitle>{'Delete this Product?'}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          {'Are you sure you want to delete this record?'}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {isAuthorized && (
          <LoadingButton
            loading={isLoading}
            variant="contained"
            onClick={handleDelete}
          >
            Delete
          </LoadingButton>
        )}
      </DialogActions>
      {!isAuthorized && (
        <Dialog open={true}>
          <DialogContent>
            <DialogContentText>
              {
                'You cannot delete this data product because it belongs to another user.'
              }
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose}>Close</Button>
          </DialogActions>
        </Dialog>
      )}
    </Dialog>
  )
}

ProductRemove.propTypes = {
  recordId: PropTypes.number,
  onRemoveSuccess: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired
}
