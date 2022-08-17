import * as React from 'react'
import Button from '@mui/material/Button'
import TextField from '@mui/material/TextField'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import LoadingButton from '@mui/lab/LoadingButton'
import Stack from '@mui/material/Stack'
import IconButton from '@mui/material/IconButton'
import { generateApiToken } from '../services/user'
import CopyIcon from '@mui/icons-material/ContentCopy'
import Snackbar from '@mui/material/Snackbar'
import PropTypes from 'prop-types'

export default function TokenDialog({ open, onClose }) {
  const [isLoading, setLoading] = React.useState(false)
  const [token, setToken] = React.useState('')
  const [copied, setCopied] = React.useState(false)

  const handleNewApi = () => {
    setLoading(true)

    generateApiToken()
      .then(res => {
        setLoading(false)
        setToken(res.data.token)
      })
      .catch(res => {
        // TODO: Tratar Error
        setLoading(false)
      })
  }
  const handleCopy = () => {
    const text = token

    if (!navigator.clipboard) {
      fallbackCopyTextToClipboard(text)
      return
    }
    navigator.clipboard.writeText(text).then(
      function () {
        // console.log('Async: Copying to clipboard was successful!');
        setCopied(true)
      },
      function (err) {
        console.error('Async: Could not copy text: ', err)
      }
    )
  }

  const fallbackCopyTextToClipboard = text => {
    const textArea = document.createElement('textarea')
    textArea.value = text

    // Avoid scrolling to bottom
    textArea.style.top = '0'
    textArea.style.left = '0'
    textArea.style.position = 'fixed'

    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    try {
      // eslint-disable-next-line no-unused-vars
      const successful = document.execCommand('copy')
      setCopied(true)
      // const msg = successful ? 'successful' : 'unsuccessful'
      // console.log('Fallback: Copying text command was ' + msg);
    } catch (err) {
      console.error('Fallback: Oops, unable to copy', err)
    }

    document.body.removeChild(textArea)
  }

  const handleCloseSnack = () => {
    setCopied(false)
  }

  const handleClose = () => {
    setToken('')
    setCopied(false)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>API Token</DialogTitle>
      <DialogContent>
        <DialogContentText>
          <p>Generate a personal token to be used in the Photo-z Server API.</p>
          <p>Only one token can be used at a time.</p>
          <p>
            By clicking on &quot;Generate new token&quot;, the old token will be
            removed.
          </p>
          <p>Copy the token and keep it in a safe place.</p>
          <p>The token will not be visible after the window is closed.</p>
        </DialogContentText>
        <LoadingButton
          loading={isLoading}
          loadingPosition="start"
          variant="contained"
          onClick={handleNewApi}
        >
          Generate API Token
        </LoadingButton>
        <Stack direction="row" spacing={2}>
          <TextField
            margin="dense"
            fullWidth
            // variant="standard"
            value={token}
            readOnly
          />
          <IconButton
            size="large"
            edge="end"
            // color="inherit"
            onClick={handleCopy}
            disabled={!token}
            variant="outlined"
          >
            <CopyIcon />
          </IconButton>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
      </DialogActions>
      <Snackbar
        open={copied}
        autoHideDuration={3000}
        onClose={handleCloseSnack}
        message="The token has been copied to the clipboard!"
      />
    </Dialog>
  )
}

TokenDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired
}
