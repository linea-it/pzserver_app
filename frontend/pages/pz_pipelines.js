import React from 'react'
import {
  Card,
  CardActionArea,
  CardMedia,
  Grid,
  Typography
} from '@mui/material'
import Head from 'next/head'
import Link from '../components/Link'
import Banner from '../components/Banner'
import useStyles from '../styles/pages/pz_pipelines'

export default function PZPipelines() {
  const classes = useStyles()

  const pipelines = [
    {
      title: 'Combine Spec-z Catalogs',
      path: '/specz_catalogs',
      background: '/interfaces/milkyway.jpg',
      description:
        'Creats a single spec-z from the multiple spatial cross-matching (all-to-all) of a list of pre-registered individual spec-z catalogs.'
    },
    {
      title: 'Training Set Maker',
      path: '/training_set_maker',
      background: '/interfaces/noirlab.jpg',
      description:
        'Creates a training set from the spatial cross-matching of a given spec-z catalog and the LSST Objects Catalogs.'
    }
  ]

  return (
    <div className={classes.root}>
      <Head>
        <title>Photo-z Server | Pipelines</title>
      </Head>
      <Banner />
      <Grid className={classes.main}>
        <Grid
          container
          justifyContent="center"
          alignItems="stretch"
          className={classes.pipelinesContainer}
        >
          {pipelines.map(item => (
            <Grid
              key={item.title}
              item
              xs={12}
              sm={6}
              md={4}
              lg={3}
              className={classes.gridApplicationLg}
            >
              <Link href={item.path}>
                <Card key={item.title}>
                  <CardActionArea>
                    <CardMedia
                      alt={item.title}
                      className={classes.media}
                      image={item.background}
                      title={item.title}
                    >
                      <Typography
                        gutterBottom
                        className={classes.titleItem}
                        variant="h4"
                        component="h2"
                      >
                        {item.title}
                      </Typography>
                      <Typography
                        gutterBottom
                        className={classes.ItemDescription}
                        variant="body1"
                        component="span"
                      >
                        {item.description}
                      </Typography>
                    </CardMedia>
                  </CardActionArea>
                </Card>
              </Link>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </div>
  )
}
