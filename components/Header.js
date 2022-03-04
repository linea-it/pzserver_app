import React from 'react'
import { useRouter } from 'next/router'
import {
  AppBar,
  Toolbar,
  List,
  ListItem,
  Grid,
  IconButton
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

  // const handlerClick = socialMedia => {
  //   let uri = ''
  //   switch (socialMedia) {
  //     case 'YouTube':
  //       uri = 'https://www.youtube.com/user/lineamcti'
  //       break
  //     case 'Twitter':
  //       uri = 'https://twitter.com/LIneA_mcti'
  //       break
  //     case 'GitHub':
  //       uri = 'https://github.com/linea-it/tno'
  //       break
  //     default:
  //       uri = 'https://www.youtube.com/user/lineamcti'
  //   }
  //   window.open(uri, '_blank')
  // }

  return (
    <div>
      <AppBar position="static" className={classes.toolbarWrapper}>
        <Toolbar className={classes.toolbar}>
          <img src="/logo.png" alt="LIneA" className={classes.logoLIneA} />
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
            <IconButton color="inherit" aria-label="YouTube" component="span">
              <YouTube />
            </IconButton>
            <IconButton color="inherit" aria-label="Twitter" component="span">
              <Twitter />
            </IconButton>
            <IconButton color="inherit" aria-label="GitHub" component="span">
              <GitHub />
            </IconButton>
          </div>
        </Grid>
      )}
    </div>
  )
}

export default Header
