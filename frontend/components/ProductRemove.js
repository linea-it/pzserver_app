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

  const handleDelete = async () => {
    setLoading(true)
    try {
      await deleteProduct(recordId)
      onRemoveSuccess()
      onClose()
    } catch (error) {
      onError(
        'Failed to remove the product. Please try again later or contact the helpdesk.'
      )
      setLoading(false)
    }
  }

  if (recordId === null) return null

  return (
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
  )
}

ProductRemove.propTypes = {
  recordId: PropTypes.number,
  productName: PropTypes.string,
  onRemoveSuccess: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired
}
