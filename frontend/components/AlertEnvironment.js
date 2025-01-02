import Alert from '@mui/material/Alert'
import AlertTitle from '@mui/material/AlertTitle'
import React from 'react'

function AlertEnvironment() {
  return (
    <Alert severity="warning">
      <AlertTitle>
        This is a development and testing version of this platform.
      </AlertTitle>
      Do not use its data or reference it in any way.
      <br />
      The production instance will be available soon.
      <br />
      For more information, please access &nbsp;
      <a
        href="https://linea-it.github.io/pz-lsst-inkind-doc/"
        target="blank"
        rel="noopener noreferrer"
      >
        https://linea-it.github.io/pz-lsst-inkind-doc/.
      </a>
    </Alert>
  )
}

export default AlertEnvironment
