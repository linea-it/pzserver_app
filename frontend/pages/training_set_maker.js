import { Typography, IconButton } from '@mui/material'
import useStyles from '../styles/pages/training_set_maker'
import InfoIcon from '@mui/icons-material/Info'

export default function TrainingSetMaker() {
  const classes = useStyles()

  return (
    <div
      className={`${classes.container}`}
      style={{ flexDirection: 'column', justifyContent: 'flex-start' }}
    >
      <Typography
        variant="h4"
        className={`${classes.title} ${classes.center}`}
        style={{ textAlign: 'center' }}
      >
        Training Set Maker
        <IconButton aria-label="info" title="Training Set Maker">
          <InfoIcon />
        </IconButton>
      </Typography>
    </div>
  )
}
