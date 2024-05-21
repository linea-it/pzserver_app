import React from 'react'
import PropTypes from 'prop-types'
import Typography from '@mui/material/Typography'

const statusLabels = {
  0: 'Registering',
  1: 'Published',
  9: 'Failed'
}

export default function ProductStatus({ value }) {
  const statusLabel = statusLabels[value] || 'Unknown'

  return <Typography>{statusLabel}</Typography>
}

ProductStatus.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
}
