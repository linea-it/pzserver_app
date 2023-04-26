import { Grid, Typography } from '@mui/material'
import Image from 'next/image'
import React from 'react'
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
          <div className={classes.images_credits}>
            {/* <Typography >Image credits: NOIRLab public images archive and LSST gallery.</Typography> */}
            <Typography variant="body2" component="span">
              <p>
                Image credits:{' '}
                <Link
                  href="https://noirlab.edu/public/images/archive/category/vro/"
                  target="_blank"
                  rel="noreferrer"
                >
                  NOIRLab public images archive
                </Link>{' '}
                and{' '}
                <Link
                  href="https://gallery.lsst.org/"
                  target="_blank"
                  rel="noreferrer"
                >
                  LSST gallery.
                </Link>{' '}
              </p>
            </Typography>
          </div>
        </Grid>
        <Grid item className={classes.marginItem}>
          <Typography>
            <span className={classes.poweredBy}>Powered By</span>
            <Link
              href="https://www.linea.org.br/"
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
