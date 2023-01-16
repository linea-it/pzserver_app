import {
  AppBar,
  Grid,
  IconButton,
  Link as MuiLink,
  List,
  ListItem,
  Menu,
  MenuItem,
  Toolbar,
  Typography
} from '@mui/material'
import { useRouter } from 'next/router'
import React from 'react'

import { GitHub, Twitter, YouTube } from '@mui/icons-material'
import MoreIcon from '@mui/icons-material/MoreVert'
import TokenDialog from '../components/TokenDialog'
import { useAuth } from '../contexts/AuthContext'
import useStyles from '../styles/components/Header'
import Link from './Link'

function Header() {
  const classes = useStyles()
  const router = useRouter()
  const { user, logout } = useAuth()
  const [anchorEl, setAnchorEl] = React.useState(null)
  const [open, setOpen] = React.useState(false)

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

  const handleMenu = event => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleTokenOpen = () => {
    // Fecha o menu
    setAnchorEl(null)
    // Abre a Dialog Token Api
    setOpen(true)
  }

  const handleTokenClose = () => {
    setOpen(false)
  }

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
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleMenu}
          >
            <MoreIcon />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right'
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right'
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleTokenOpen}>API Token</MenuItem>
            <MenuItem onClick={logout}>Logout</MenuItem>
          </Menu>
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
              href="https://twitter.com/LIneA_org"
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
      <TokenDialog open={open} onClose={handleTokenClose}></TokenDialog>
    </div>
  )
}

export default Header
