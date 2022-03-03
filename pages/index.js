import Head from 'next/head'
import {
  Grid,
  IconButton,
  Card,
  CardActionArea,
  CardMedia,
  Typography
} from '@material-ui/core'
import { YouTube, Twitter, GitHub } from '@material-ui/icons'
import useStyles from '../styles/pages/index'

export default function Index() {
  const classes = useStyles()

  const handlerClick = socialMedia => {
    let uri = ''
    switch (socialMedia) {
      case 'YouTube':
        uri = 'https://www.youtube.com/user/lineamcti'
        break
      case 'Twitter':
        uri = 'https://twitter.com/LIneA_mcti'
        break
      case 'GitHub':
        uri = 'https://github.com/linea-it/tno'
        break
      default:
        uri = 'https://www.youtube.com/user/lineamcti'
    }
    window.open(uri, '_blank')
  }

  const interfaces = [
    {
      title: 'Upload',
      path: '/upload',
      background: '/interfaces/upload.jpg'
    },
    {
      title: 'LSST PZ Data Products',
      path: '/lsst-data-products',
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
      <Grid className={classes.banner}>
        <Grid
          container
          direction="row"
          justifyContent="space-between"
          alignItems="flex-start"
          className={classes.container}
        >
          <Grid item xs={12} className={classes.titleWrapper}>
            <h1 className={classes.title}>Photo-Z Server</h1>
          </Grid>
        </Grid>
        <div className={classes.socialWrapper}>
          <IconButton
            onClick={() => {
              handlerClick('Youtube')
            }}
            color="inherit"
            aria-label="YouTube"
            component="span"
          >
            <YouTube />
          </IconButton>
          <IconButton
            onClick={() => {
              handlerClick('Twitter')
            }}
            color="inherit"
            aria-label="Twitter"
            component="span"
          >
            <Twitter />
          </IconButton>
          <IconButton
            onClick={() => {
              handlerClick('GitHub')
            }}
            color="inherit"
            aria-label="GitHub"
            component="span"
          >
            <GitHub />
          </IconButton>
        </div>
      </Grid>
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
              <Card>
                <CardActionArea to={item.path}>
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
            </Grid>
          ))}
        </Grid>
      </Grid>
    </div>
  )
}
