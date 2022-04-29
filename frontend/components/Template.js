import * as React from 'react'
import { Paper } from '@mui/material'
import Grid from '@mui/material/Grid'
import Divider from '@mui/material/Divider'
import Typography from '@mui/material/Typography'
import useStyles from '../styles/pages/template'

export default function Products() {
  const classes = useStyles()

  return (
    // Baseado neste template: https://mira.bootlab.io/dashboard/analytics
    <Paper className={classes.root}>
      <Grid container className={classes.gridTitle}>
        <Grid item xs={4}>
          {/* TODO: Aqui deve entrar o BREADCRUMB */}
          <Typography variant="h3" className={classes.title}>
            Page Title
          </Typography>
        </Grid>
        <Grid item xs={4}>
          {/* TODO: Aqui deve entrar botões de ações da pagina */}
        </Grid>
      </Grid>
      <Divider className={classes.titleDivider} />
      <Grid container className={classes.gridContent}>
        <Grid item xs={12}>
          <Typography variant="h3">Grid Content</Typography>
        </Grid>
      </Grid>
    </Paper>
  )
}
