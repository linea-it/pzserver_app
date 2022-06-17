import React from 'react'
import PropTypes from 'prop-types'
import Backdrop from '@mui/material/Backdrop'
import CircularProgress from '@mui/material/CircularProgress'

export default function Loading({ isLoading }) {
  // const theme = useTheme()

  return (
    <Backdrop
      sx={{ color: '#fff', zIndex: theme => theme.zIndex.drawer + 1 }}
      open={isLoading}
    >
      <CircularProgress color="inherit" />
    </Backdrop>
  )
}
Loading.propTypes = {
  isLoading: PropTypes.bool.isRequired
}
