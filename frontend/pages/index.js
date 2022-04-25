import Head from 'next/head'
import {
  Grid,
  Card,
  CardActionArea,
  CardMedia,
  Typography
} from '@material-ui/core'
import Link from '../components/Link'
import useStyles from '../styles/pages/index'

export default function Index() {
  const classes = useStyles()

  const interfaces = [
    {
      title: 'Upload',
      path: '/upload',
      background: '/interfaces/upload.jpg'
    },
    {
      title: 'LSST PZ Data Products',
      path: '/products',
      background: '/interfaces/lsst-dp.jpg'
    },
    {
      title: 'User-generated Data Products',
      path: '/user-data-products',
      background: '/interfaces/user-dp.jpg'
    }
  ]

  return (
    <div className={classes.root}>
      <Head>
        <title>Photo-Z Server | Home</title>
      </Head>
      <Grid className={classes.main}>
        <Grid
          container
          justifyContent="center"
          alignItems="stretch"
          className={classes.interfaceContainer}
        >
          {interfaces.map(item => (
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
                <Card>
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
