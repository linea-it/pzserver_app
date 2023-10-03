import { Typography, IconButton } from '@mui/material'
import useStyles from '../styles/pages/specz_catalogs'
import InfoIcon from '@mui/icons-material/Info'

export default function SpeczCatalogs() {
  const classes = useStyles()

  return (
    <div
      className={`${classes.container} flex alignCenter`}
      style={{ flexDirection: 'column', justifyContent: 'center' }}
    >
      <Typography
        variant="h4"
        className={`${classes.title} ${classes.center}`}
        style={{ textAlign: 'center' }}
      >
        Combine Spec-z Catalogs
        <IconButton aria-label="info" title="Combine Spec-z Catalogs">
          <InfoIcon />
        </IconButton>
      </Typography>
    </div>
  )
}
