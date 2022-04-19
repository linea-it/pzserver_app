import React from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'
import {
  AppBar,
  Toolbar,
  List,
  ListItem,
  Grid,
  Link as MuiLink
} from '@material-ui/core'
import { YouTube, Twitter, GitHub } from '@material-ui/icons'
import Link from './Link'
import useStyles from '../styles/components/Header'

function Header() {
  const classes = useStyles()
  const route = useRouter()

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
          <Image src="/logo.png" alt="LIneA" width={64} height={64} />
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
        </Toolbar>
      </AppBar>

      {route.pathname === '/' && (
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
