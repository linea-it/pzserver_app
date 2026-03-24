import * as React from 'react'

import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'

import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
import Link from '@mui/material/Link'
import Paper from '@mui/material/Paper'
import Snackbar from '@mui/material/Snackbar'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import ProductGrid from '../components/ProductGrid'
import ProductTypeSelect from '../components/ProductTypeSelect'
import ReleaseSelect from '../components/ReleaseSelect'
import SearchField from '../components/SearchField'
import useStyles from '../styles/pages/products'
import { buildLoginUrl } from '../utils/redirect'

export default function Products() {
  const classes = useStyles()
  const router = useRouter()

  const applySearch = React.useMemo(() => {
    if (typeof window !== 'undefined') {
      return JSON.parse(sessionStorage.getItem('apply_search') || 'false')
    } else {
      return false
    }
  }, [])

  const applyPagination = React.useMemo(() => {
    if (typeof window !== 'undefined') {
      return JSON.parse(sessionStorage.getItem('apply_pagination') || 'false')
    } else {
      return false
    }
  }, [])

  // Clear flags after they are used
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('apply_search', 'false')
      sessionStorage.setItem('apply_pagination', 'false')
    }
  }, [])

  // Load initial state from sessionStorage only if apply_search is true
  const [search, setSearch] = React.useState(() => {
    if (typeof window !== 'undefined' && applySearch) {
      const value = sessionStorage.getItem('user_products_search') || ''
      console.log('Loading search from sessionStorage: ', value)
      return value
    }
    return ''
  })

  const [filters, setFilters] = React.useState(() => {
    if (typeof window !== 'undefined' && applySearch) {
      const saved = sessionStorage.getItem('user_products_filters')
      if (saved) {
        try {
          return {
            ...JSON.parse(saved),
            official_product: false,
            status__in: '0, 1, 3, 9'
          }
        } catch (e) {
          console.error('Error parsing saved filters:', e)
        }
      }
    }
    return {
      release: '',
      product_type: '',
      official_product: false,
      status__in: '0, 1, 3, 9'
    }
  })

  // Save to sessionStorage when filters or search change
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('user_products_search', search)
    }
  }, [search])

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(
        'user_products_filters',
        JSON.stringify({
          release: filters.release,
          product_type: filters.product_type
        })
      )
    }
  }, [filters.release, filters.product_type])

  const [errorSnackbar, setErrorSnackbar] = React.useState({
    open: false,
    message: ''
  })

  const handleOpenErrorSnackbar = message => {
    setErrorSnackbar({
      open: true,
      message
    })
  }

  return (
    // Baseado neste template: https://mira.bootlab.io/dashboard/analytics
    <Paper className={classes.root}>
      <Grid container className={classes.gridTitle}>
        <Grid item xs={4}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">
              User-generated Data Products
            </Typography>
          </Breadcrumbs>
          <Box
            sx={{
              mt: 1,
              mb: 1,
              p: 1
            }}
            alignItems="center"
            justifyContent="space-between"
          >
            <Stack
              direction="row"
              justifyContent="flex-start"
              alignItems="center"
              spacing={2}
            >
              <ArrowBackIosIcon
                onClick={() => {
                  router.back()
                }}
                color="primary"
                cursor="pointer"
              />
              <Typography variant="h3" className={classes.title}>
                User-generated Data Products
              </Typography>
            </Stack>
          </Box>
        </Grid>
        <Grid item xs={4}>
          {/* TODO: Aqui deve entrar botões de ações da pagina */}
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              router.push('/product/new')
            }}
          >
            New Product
          </Button>
        </Grid>
      </Grid>
      <Card>
        <CardContent>
          <Grid container className={classes.gridContent}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                <FormControl sx={{ mt: 1, minWidth: '200px' }}>
                  <ReleaseSelect
                    value={filters.release}
                    onChange={value => {
                      setFilters({
                        ...filters,
                        release: value
                      })
                    }}
                    disabled={search !== ''}
                    allowAll={true}
                    noRelease={true}
                  />
                </FormControl>
                <FormControl sx={{ m: 1, minWidth: '200px' }}>
                  <ProductTypeSelect
                    value={filters.product_type}
                    onChange={value => {
                      setFilters({
                        ...filters,
                        product_type: value
                      })
                    }}
                    disabled={search !== ''}
                    allowAll={true}
                  />
                </FormControl>
                {/* TODO: Empurrar o Search para a direita */}
                <SearchField
                  initialValue={search}
                  onChange={query => setSearch(query)}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <ProductGrid
                query={search}
                filters={filters}
                storageKey="user_products"
                applyPagination={applyPagination}
                onError={error => {
                  console.error('Error loading products:', error)
                  handleOpenErrorSnackbar(
                    'Error loading products. Please try again.'
                  )
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      <Snackbar
        open={errorSnackbar.open}
        autoHideDuration={6000}
        onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
      >
        <Alert
          onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
          severity="error"
          sx={{ width: '100%' }}
        >
          {errorSnackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  )
}

export const getServerSideProps = async ctx => {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (!token) {
    // Captura a URL atual para redirecionamento pós-login
    const currentUrl = ctx.resolvedUrl || ctx.req.url
    const loginUrl = buildLoginUrl(currentUrl)
    return {
      redirect: {
        destination: loginUrl,
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
}
