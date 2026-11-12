import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Stack,
  TextField,
  Typography
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

const statusLabels = {
  active: 'Active',
  expired: 'Expired',
  revoked: 'Revoked'
}
const formatDate = value =>
  value ? new Date(value).toLocaleString() : 'Not renewed yet'

export default function ConnectedApplications() {
  const { isAuthenticated } = useAuth()
  const [accesses, setAccesses] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [selected, setSelected] = useState(null)
  const [action, setAction] = useState('revoke')
  const [name, setName] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const response = await api.get('/api/device-access/')
      setAccesses(response.data.filter(access => access.status !== 'revoked'))
    } catch {
      setError('Unable to load connected applications. Sign in and try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) load()
    else setAccesses([])
  }, [isAuthenticated])

  function select(access, nextAction) {
    setSelected(access)
    setAction(nextAction)
    setName(access.name)
    setError('')
    setMessage('')
  }

  async function save() {
    setBusy(true)
    setError('')
    try {
      const url = `/api/device-access/${selected.id}/`
      if (action === 'rename') await api.patch(url, { name: name.trim() })
      else await api.delete(url)
      setSelected(null)
      setMessage(
        action === 'rename'
          ? 'Access name updated.'
          : 'Access revoked. A new browser authorization is required to reconnect.'
      )
      await load()
    } catch {
      setError('Unable to update this access. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Box
      component="main"
      sx={{
        flex: 1,
        width: '100%',
        maxWidth: 1120,
        mx: 'auto',
        px: { xs: 2, md: 4 },
        py: { xs: 3, md: 4 }
      }}
    >
      <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 1 }}>
        Connected applications
      </Typography>
      <Typography color="text.secondary" sx={{ maxWidth: 760, mb: 3 }}>
        Manage notebooks and Python environments you authorized in your browser.
        Revoking an access disconnects that environment and prevents token
        renewal. Your web login and other connections remain available.
      </Typography>
      {!isAuthenticated ? (
        <Button
          variant="contained"
          href="/login?returnUrl=%2Fconnected_applications"
        >
          Sign in to PzServer
        </Button>
      ) : (
        <Stack spacing={2}>
          {error && !selected && <Alert severity="error">{error}</Alert>}
          {message && <Alert severity="success">{message}</Alert>}
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            spacing={2}
          >
            <Typography variant="h6" component="h2">
              Authorized environments
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              disabled={loading || busy}
              onClick={load}
            >
              Reload list
            </Button>
          </Stack>
          {loading ? (
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              role="status"
              sx={{ py: 2 }}
            >
              <CircularProgress
                size={22}
                aria-label="Loading connected applications"
              />
              <Typography color="text.secondary">
                Loading connections…
              </Typography>
            </Stack>
          ) : accesses.length === 0 && !error ? (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" component="h3">
                  No connected applications
                </Typography>
                <Typography color="text.secondary">
                  Authorize a Python environment to see it here.
                </Typography>
              </CardContent>
            </Card>
          ) : (
            accesses.map(access => (
              <Card key={access.id} variant="outlined" sx={{ borderRadius: 2 }}>
                <CardContent
                  sx={{
                    p: { xs: 2, sm: 3 },
                    '&:last-child': { pb: { xs: 2, sm: 3 } }
                  }}
                >
                  <Stack
                    direction={{ xs: 'column', sm: 'row' }}
                    spacing={3}
                    justifyContent="space-between"
                    alignItems={{ xs: 'stretch', sm: 'center' }}
                  >
                    <Box sx={{ minWidth: 0 }}>
                      <Stack
                        direction="row"
                        spacing={1.5}
                        alignItems="center"
                        sx={{ flexWrap: 'wrap', rowGap: 1, mb: 1 }}
                      >
                        <Typography
                          variant="h6"
                          component="h3"
                          sx={{ overflowWrap: 'anywhere' }}
                        >
                          {access.name}
                        </Typography>
                        <Chip
                          size="small"
                          variant="outlined"
                          label={statusLabels[access.status] || access.status}
                          color={
                            access.status === 'active' ? 'success' : 'default'
                          }
                        />
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        {access.application} · Connection{' '}
                        {access.id.slice(0, 8)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Authorized: {formatDate(access.authorized_at)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Last renewal: {formatDate(access.last_renewed_at)}
                      </Typography>
                      {access.revoked_at && (
                        <Typography variant="body2" color="text.secondary">
                          Revoked: {formatDate(access.revoked_at)}
                        </Typography>
                      )}
                    </Box>
                    <Stack direction="row" spacing={1} sx={{ flexShrink: 0 }}>
                      <Button
                        disabled={busy}
                        onClick={() => select(access, 'rename')}
                      >
                        Rename
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        disabled={busy || access.status === 'revoked'}
                        onClick={() => select(access, 'revoke')}
                      >
                        Revoke access
                      </Button>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            ))
          )}
        </Stack>
      )}
      <Dialog
        fullWidth
        maxWidth="sm"
        open={Boolean(selected)}
        onClose={() => {
          if (!busy) setSelected(null)
        }}
        aria-labelledby="connection-dialog-title"
      >
        <DialogTitle id="connection-dialog-title">
          {action === 'rename' ? 'Rename connection' : 'Revoke access?'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {action === 'rename' ? (
            <>
              <DialogContentText sx={{ mb: 2 }}>
                Choose a label you recognize, such as “Local notebook” or
                “Jupyter Rubin”. This label does not verify the environment’s
                identity.
              </DialogContentText>
              <TextField
                autoFocus
                fullWidth
                label="Connection name"
                value={name}
                onChange={event => setName(event.target.value)}
                inputProps={{ maxLength: 100 }}
                disabled={busy}
              />
            </>
          ) : (
            <DialogContentText>
              Revoke {selected?.name}? Its current access and renewal tokens
              will stop working. This environment will need your approval in the
              browser to connect again. Requests already in progress may finish.
            </DialogContentText>
          )}
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setSelected(null)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color={action === 'revoke' ? 'error' : 'primary'}
            disabled={busy || (action === 'rename' && !name.trim())}
            onClick={save}
          >
            {busy
              ? 'Saving…'
              : action === 'rename'
              ? 'Save name'
              : 'Revoke access'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
