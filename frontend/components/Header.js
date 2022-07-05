import React from 'react'
import { useRouter } from 'next/router'
import {
  AppBar,
  Toolbar,
  List,
  ListItem,
  Grid,
  Link as MuiLink,
  Typography,
  Button
} from '@mui/material'
import { YouTube, Twitter, GitHub } from '@mui/icons-material'
import Link from './Link'
import useStyles from '../styles/components/Header'
import { useAuth } from '../contexts/AuthContext'

function Header() {
  const classes = useStyles()
  const router = useRouter()
  const { user, logout } = useAuth()

  const menus = [
    {
      description: 'Home',
      href: '/'
    },
    {
      description: 'About',
      href: '/about'
    },
    {
      description: 'Tutorials',
      href: '/tutorials'
    },
    {
      description: 'Contact',
      href: '/contact'
    }
  ]

  return (
    <div>
      <AppBar position="static" className={classes.appbar}>
        <Toolbar className={classes.toolbar}>
          <List className={classes.menuList}>
            {menus.map(menu => (
              <ListItem key={menu.href} className={classes.menuListItem}>
                <Link href={menu.href} className={classes.menuLink}>
                  {menu.description}
                </Link>
              </ListItem>
            ))}
          </List>
          <div className={classes.separator} />
          <Typography>{user?.username}</Typography>
          <Button onClick={logout}>Logout</Button>
        </Toolbar>
      </AppBar>

      {router.pathname === '/' && (
        <Grid className={classes.banner}>
          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="flex-start"
            className={classes.container}
          >
            <Grid item xs={12} className={classes.titleWrapper}>
              {/* <h1 className={classes.title}>Photo-z Server</h1> */}
              <Typography variant="h1" className={classes.title}>
                Photo-z Server
              </Typography>
              <Typography variant="body1" display="block">
                <p>
                  Welcome to the Photo-z Server! This is an ancillary service
                  available to Rubin Science Platform users to host lightweight
                  data products related to photo-zs.
                </p>
                <p>
                  Click{' '}
                  <MuiLink
                    variant="body1"
                    component="button"
                    onClick={e => {
                      router.push('/about')
                    }}
                  >
                    here
                  </MuiLink>{' '}
                  for more details.
                </p>
              </Typography>
              {/* <Grid item xs={12}>
              <Typography variant="body1" component="span">
                <p>
                  Welcome to the Photo-z Server! This is an ancillary service
                  available to Rubin Science Platform users to host lightweight
                  data products related to photo-zs.
                </p>
                <p>
                  Click{' '}
                  <MuiLink
                    variant="body1"
                    component="button"
                    onClick={e => {
                      router.push('/about')
                    }}
                  >
                    here
                  </MuiLink>{' '}
                  for more details.
                </p>
              </Typography>
            </Grid> */}
            </Grid>
          </Grid>
          <div className={classes.socialWrapper}>
            <MuiLink
              className={classes.social}
              href="https://www.youtube.com/user/lineamcti"
              target="_blank"
              color="inherit"
              rel="noreferrer"
            >
              <YouTube />
            </MuiLink>
            <MuiLink
              className={classes.social}
              href="https://twitter.com/LIneA_mcti"
              target="_blank"
              color="inherit"
              rel="noreferrer"
            >
              <Twitter />
            </MuiLink>
            <MuiLink
              className={classes.social}
              href="https://github.com/linea-it/pz-server"
              target="_blank"
              color="inherit"
              rel="noreferrer"
            >
              <GitHub />
            </MuiLink>
          </div>
        </Grid>
      )}
    </div>
  )
}

export default Header
