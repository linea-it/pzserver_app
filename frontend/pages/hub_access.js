import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

export default function HubAccess() {
  const { isAuthenticated } = useAuth()
  const [hubs, setHubs] = useState([])
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [selected, setSelected] = useState(null)

  async function load() {
    setLoading(true)
    try {
      const response = await api.get('/api/hub-access/')
      setHubs(response.data)
    } catch {
      setError('Unable to load JupyterHubs. Sign in to PzServer and try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) load()
  }, [isAuthenticated])

  async function save(hub, enabled) {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await api.put(`/api/hub-access/${hub.id}/`, {
        enabled,
        signature: hub.signature
      })
      setSelected(null)
      setMessage(
        enabled ? 'JupyterHub access authorized.' : 'JupyterHub access revoked.'
      )
      await load()
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(
        typeof detail === 'string'
          ? detail
          : 'Unable to save. Reload the list and try again.'
      )
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
        JupyterHub access
      </Typography>
      <Typography
        color="text.secondary"
        sx={{ maxWidth: 760, mb: 3, lineHeight: 1.7 }}
      >
        Choose which partner notebooks may access your PzServer account without
        entering a separate PzServer token. Your existing product permissions
        still apply. You can revoke access at any time.
      </Typography>
      {!isAuthenticated ? (
        <Button variant="contained" href="/login?returnUrl=%2Fhub_access">
          Sign in to PzServer
        </Button>
      ) : (
        <Stack spacing={2}>
          {error && <Alert severity="error">{error}</Alert>}
          {message && <Alert severity="success">{message}</Alert>}
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            spacing={2}
          >
            <Typography variant="h6" component="h2">
              Partner JupyterHubs
            </Typography>
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              disabled={loading || busy}
              onClick={() => {
                setError('')
                load()
              }}
              sx={{ flexShrink: 0 }}
            >
              Reload list
            </Button>
          </Stack>
          {loading && (
            <Stack
              direction="row"
              spacing={1.5}
              alignItems="center"
              sx={{ py: 2 }}
              role="status"
            >
              <CircularProgress size={22} aria-label="Loading JupyterHubs" />
              <Typography color="text.secondary">
                Loading JupyterHubs…
              </Typography>
            </Stack>
          )}
          {!loading && !error && hubs.length === 0 && (
            <Box
              sx={{ p: 3, border: 1, borderColor: 'divider', borderRadius: 2 }}
            >
              <Typography sx={{ fontWeight: 500 }}>
                No partner JupyterHubs yet
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                Registered partners will appear here so you can manage their
                access.
              </Typography>
            </Box>
          )}
          {hubs.map(hub => (
            <Card key={hub.id} variant="outlined" sx={{ borderRadius: 2 }}>
              <CardContent
                sx={{
                  p: { xs: 2, sm: 3 },
                  '&:last-child': { pb: { xs: 2, sm: 3 } }
                }}
              >
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  spacing={3}
                  alignItems={{ xs: 'stretch', sm: 'center' }}
                  justifyContent="space-between"
                >
                  <Box sx={{ minWidth: 0 }}>
                    <Stack
                      direction="row"
                      spacing={1.5}
                      alignItems="center"
                      sx={{ flexWrap: 'wrap', rowGap: 1, mb: 0.75 }}
                    >
                      <Typography variant="h6" component="h3">
                        {hub.name}
                      </Typography>
                      <Chip
                        size="small"
                        variant="outlined"
                        color={
                          !hub.available
                            ? 'warning'
                            : hub.authorized
                            ? 'success'
                            : 'default'
                        }
                        label={
                          !hub.available
                            ? 'Unavailable'
                            : hub.authorized
                            ? 'Authorized'
                            : 'Not authorized'
                        }
                      />
                    </Stack>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ overflowWrap: 'anywhere' }}
                    >
                      {hub.public_url}
                    </Typography>
                    {!hub.available && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1 }}
                      >
                        Access is currently blocked by the administrator.
                      </Typography>
                    )}
                  </Box>
                  {hub.authorized ? (
                    <Button
                      variant="outlined"
                      color="error"
                      disabled={busy}
                      onClick={() => save(hub, false)}
                      sx={{ flexShrink: 0 }}
                    >
                      Revoke access
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      disableElevation
                      disabled={busy || !hub.available}
                      onClick={() => setSelected(hub)}
                      sx={{ flexShrink: 0 }}
                    >
                      Authorize access
                    </Button>
                  )}
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}
      <Dialog
        fullWidth
        maxWidth="sm"
        open={Boolean(selected)}
        onClose={() => {
          if (!busy) setSelected(null)
        }}
      >
        <DialogTitle>Authorize JupyterHub access?</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error">{error}</Alert>}
          Allow notebooks from {selected?.name} ({selected?.public_url}) to
          access your PzServer account using your Hub identity and existing
          permissions?
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setSelected(null)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disableElevation
            disabled={busy}
            onClick={() => save(selected, true)}
          >
            Authorize
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
