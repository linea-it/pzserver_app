import React from 'react'
import Image from 'next/image'
import { Typography, Grid } from '@material-ui/core'
import Link from '../components/Link'
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
          <Link href="https://www.lsst.org/" target="_blank">
            <Image
              src="/rubin.png"
              alt="LIneA"
              width={80}
              height={50}
              className={classes.rubinLogo}
            />
          </Link>
          <Link href="https://data.lsst.cloud/" target="_blank">
            <Typography className={classes.rsp}>RSP</Typography>
          </Link>
        </Grid>
        <Grid item className={classes.marginItem}>
          <Typography>
            <span className={classes.poweredBy}>Powered By</span>
            <Link
              href="https://www.linea.gov.br/"
              target="_blank"
              className={classes.logoLink}
            >
              <Image
                src="/logo.png"
                alt="LIneA"
                width={52}
                height={52}
                className={classes.logoFooter}
              />
            </Link>
          </Typography>
        </Grid>
      </Grid>
    </footer>
  )
}
export default Footer
