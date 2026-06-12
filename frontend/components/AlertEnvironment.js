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
      The production instance is available at:
      <a
        href="https://pzserver.linea.org.br/"
        target="blank"
        rel="noopener noreferrer"
      >
        https://pzserver.linea.org.br/
      </a>
      <br />
      For more information, please access &nbsp;
      <a
        href="https://docs.linea.org.br/en/sci-platforms/pz_server.html"
        target="blank"
        rel="noopener noreferrer"
      >
        https://docs.linea.org.br/en/sci-platforms/pz_server.html
      </a>
    </Alert>
  )
}

export default AlertEnvironment
