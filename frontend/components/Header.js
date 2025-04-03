import MenuIcon from '@mui/icons-material/Menu'
import {
  AppBar,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  Menu,
  MenuItem,
  Link as MuiLink,
  Toolbar,
  Typography
} from '@mui/material'
import Box from '@mui/material/Box'
import Divider from '@mui/material/Divider'
import Drawer from '@mui/material/Drawer'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import { useRouter } from 'next/router'

import {
  // GitHub,
  // Twitter,
  // YouTube,
  Brightness4,
  Brightness7,
  Logout
} from '@mui/icons-material'
import MoreIcon from '@mui/icons-material/MoreVert'
import PropTypes from 'prop-types'
import React from 'react'
import TokenDialog from '../components/TokenDialog'
import { useAuth } from '../contexts/AuthContext'
import useStyles from '../styles/components/Header'
import Link from './Link'

function Header(props) {
  const { window, darkMode, setDarkMode } = props
  const classes = useStyles()
  const router = useRouter()
  const { user, logout } = useAuth()
  const [anchorEl, setAnchorEl] = React.useState(null)
  const [open, setOpen] = React.useState(false)
  const [mobileOpen, setMobileOpen] = React.useState(false)

  const drawerWidth = 240
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
    setAnchorEl(null)
    setOpen(true)
  }

  const handleTokenClose = () => {
    setOpen(false)
  }

  const handleToggleDarkMode = () => {
    setDarkMode(prevMode => {
      const newMode = !prevMode
      localStorage.setItem('darkMode', newMode ? '1' : '0')
      return newMode
    })
  }

  const handleDrawerToggle = () => {
    setMobileOpen(prevState => !prevState)
  }

  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        Photo-z Server
      </Typography>
      <Divider />
      <List>
        {menus.map((item, idx) => (
          <MuiLink
            key={`navitem-${idx}-item`}
            href={item.href}
            underline="none"
            color="inherit"
          >
            <ListItem disablePadding>
              <ListItemButton>
                <ListItemText primary={item.description} href={item.href} />
              </ListItemButton>
            </ListItem>
          </MuiLink>
        ))}
      </List>
    </Box>
  )

  const container =
    window !== undefined ? () => window().document.body : undefined

  return (
    <div>
      <AppBar position="static" className={classes.appbar}>
        <Toolbar className={classes.toolbar}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <List className={classes.menuList}>
              {menus.map(menu => (
                <ListItem key={menu.href} className={classes.menuListItem}>
                  <Link href={menu.href} className={classes.menuLink}>
                    {menu.description}
                  </Link>
                </ListItem>
              ))}
            </List>
          </Box>
          <div className={classes.separator} />
          <Typography>{user?.username}</Typography>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleToggleDarkMode}
          >
            {darkMode ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
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
            <MenuItem onClick={logout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <Typography variant="inherit">Logout</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <nav>
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth
            }
          }}
        >
          {drawer}
        </Drawer>
      </nav>
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
          {/* <div className={classes.socialWrapper}>
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
          </div> */}
        </Grid>
      )}
      <TokenDialog open={open} onClose={handleTokenClose}></TokenDialog>
    </div>
  )
}

Header.propTypes = {
  window: PropTypes.Any,
  darkMode: PropTypes.bool.isRequired,
  setDarkMode: PropTypes.func.isRequired
}

export default Header
