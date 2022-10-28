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
export default function ProductRemove({ productId, onOk, onCancel, onError }) {
  const [isLoading, setLoading] = React.useState(false)
  const handleDelete = React.useCallback(
    async function () {
      setLoading(true)
      return await deleteProduct(productId)
        .then(res => {
          // setLoading(false)
        })
        .catch(res => {
          if (res.response.status === 403) {
            onError(
              'this product cannot be removed, please make sure you own it and try again or contact the helpdesk'
            )
          } else {
            onError(
              'Failed to remove the product, please try again later or contact the helpdesk.'
            )
          }
        })
        .finally(() => {
          setLoading(false)
          onOk()
        })
    },
    [onError, onOk, productId]
  )

  if (productId === null) return null

  return (
    <Dialog open={true}>
      <DialogTitle>{'Delete this Product?'}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          {'Are you sure you want to delete this record?'}{' '}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
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
  productId: PropTypes.number,
  onOk: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired
}
