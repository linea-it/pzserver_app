import Head from 'next/head'
import {
  Grid,
  Card,
  CardActionArea,
  CardMedia,
  Typography
} from '@mui/material'
import Link from '../components/Link'
import useStyles from '../styles/pages/index'
import { parseCookies } from 'nookies'

export default function Index() {
  const classes = useStyles()

  const interfaces = [
    {
      title: 'LSST PZ Data Products',
      path: '/oficial_products',
      background: '/interfaces/lsst-dp.jpg'
    },
    {
      title: 'User-generated Data Products',
      path: '/user_products',
      background: '/interfaces/user-dp.jpg'
    }
  ]

  return (
    <div className={classes.root}>
      <Head>
        <title>Photo-z Server | Home</title>
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

export const getServerSideProps = async ctx => {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (!token) {
    return {
      redirect: {
        destination: '/login',
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
}
