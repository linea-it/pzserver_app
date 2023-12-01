import * as React from 'react'

import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'

import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Button from '@mui/material/Button'
import Paper from '@mui/material/Paper'
import Link from '@mui/material/Link'
import Stack from '@mui/material/Stack'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'

import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import ProductGrid from '../components/ProductGrid'
import ProductTypeSelect from '../components/ProductTypeSelect'
import ReleaseSelect from '../components/ReleaseSelect'
import SearchField from '../components/SearchField'
import { useAuth } from '../contexts/AuthContext'
import useStyles from '../styles/pages/products'

export default function Products() {
  const classes = useStyles()
  const router = useRouter()
  const { user } = useAuth()

  const [search, setSearch] = React.useState('')
  const [filters, setFilters] = React.useState({
    release: '',
    product_type: '',
    official_product: true,
    status: 1 // Published
  })

  return (
    // Baseado neste template: https://mira.bootlab.io/dashboard/analytics
    <Paper className={classes.root} elevation={3}>
      <Grid container className={classes.gridTitle}>
        <Grid item xs={4}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link color="inherit" href="/">
              Home
            </Link>
            <Typography color="textPrimary">
              Rubin Observatory PZ Data Products
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
                Rubin Observatory PZ Data Products
              </Typography>
            </Stack>
          </Box>
        </Grid>
        <Grid item xs={4}>
          {/* TODO: Aqui deve entrar botões de ações da pagina */}

          {user?.is_admin === true && (
            <Button
              variant="contained"
              color="primary"
              onClick={e => {
                router.push('/product/new')
              }}
            >
              New Product
            </Button>
          )}
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
                <SearchField onChange={query => setSearch(query)} />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <ProductGrid query={search} filters={filters} />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Paper>
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
