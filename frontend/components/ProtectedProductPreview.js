import { useEffect, useState } from 'react'
import { Alert, CardMedia } from '@mui/material'
import { api } from '../services/api'

export default function ProtectedProductPreview({ fileId }) {
  const [source, setSource] = useState(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let active = true
    let objectUrl
    setSource(null)
    setFailed(false)
    api.get(`/api/product-files/${fileId}/content/`, { responseType: 'text' }).then(response => {
      if (!active) return
      objectUrl = URL.createObjectURL(new Blob([response.data], { type: 'text/html' }))
      setSource(objectUrl)
    }).catch(() => {
      if (active) setFailed(true)
    })
    return () => {
      active = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [fileId])

  if (failed) return <Alert severity="error">Unable to load description.</Alert>
  if (!source) return null
  return (
    <CardMedia
      component="iframe"
      title="Product description"
      src={source}
      sandbox=""
      height="800"
      sx={{ border: 'none', maxWidth: '100%' }}
    />
  )
}
