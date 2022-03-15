import React from 'react'
import Image from 'next/image'
import { Typography, Grid } from '@material-ui/core'
import useStyles from '../styles/components/Footer'

function Footer() {
  const classes = useStyles()

  return (
    <footer className={classes.root}>
      <Grid
        container
        direction="row"
        justifyContent="space-between"
        alignItems="center"
      >
        <Grid item className={classes.marginItem}>
          <Typography>
            <span className={classes.poweredBy}>Development</span>{' '}
            <span className={classes.versionLink}>1.0.0</span>
          </Typography>
        </Grid>
        <Grid item className={classes.marginItem}>
          <Typography>
            <span className={classes.poweredBy}>Powered by</span>
            <a
              href="https://www.linea.gov.br/"
              target="blank"
              className={classes.logoLink}
            >
              <Image
                src="/logo.png"
                alt="LIneA"
                width={52}
                height={52}
                className={classes.logoFooter}
              />
            </a>
          </Typography>
        </Grid>
      </Grid>
    </footer>
  )
}
export default Footer
