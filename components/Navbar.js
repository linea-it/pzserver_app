import React from 'react'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Link from './Link'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import useStyles from '../styles/components/Navbar'

function Header() {
  const classes = useStyles()

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
  )
}

export default Header
