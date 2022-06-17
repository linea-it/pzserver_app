import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import useStyles from '../../styles/pages/product'

import {
  Container,
  Grid,
  Typography,
  Paper,
  Box,
  Button,
  Chip,
  Stack
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import VerifiedIcon from '@mui/icons-material/Verified'
import { getProducts } from '../../services/product'
import moment from 'moment'
import prettyBytes from 'pretty-bytes'
import Loading from '../../components/Loading'
import DefaultErrorPage from 'next/error'

export default function Product() {
  const classes = useStyles()
  const router = useRouter()
  const { pid } = router.query
  const [data, setData] = useState(null)
  const [isLoading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)

    getProducts({
      filters: { internal_name: pid }
    })
      .then(res => {
        if (res.count === 1) {
          // Apresenta a interface de Produtos
          setData(res.results[0])
        } else {
          // Retorna error 404
          // TODO: Tratar os errors e apresentar.
          console.log(
            'Mais de um registro encontrado para o mesmo internal name.'
          )
        }
        setLoading(false)
        // router.push('/404')
      })
      .catch(res => {
        // Retorna error 404
        // TODO: Tratar os errors e apresentar.
        setLoading(false)
      })
  }, [pid])

  // TODO: Melhorar a apresentação do Loading
  if (isLoading) return <Loading isLoading={isLoading} />
  // TODO: Criar uma interface de error.
  if (!data) return <DefaultErrorPage statusCode={404} />

  return (
    <Container className={classes.root}>
      <Box className={classes.pageHeader}>
        <Typography variant="h6">Product</Typography>
      </Box>
      <Box component="form" noValidate autoComplete="off">
        <Grid container spacing={3}>
          <Grid item xs={8}>
            <Paper elevation={2} className={classes.paper}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={2}
              >
                <Typography variant="h4">{data.display_name}</Typography>

                {data.official_product !== '' && (
                  <Chip
                    variant="outlined"
                    color="success"
                    label="Official Product"
                    icon={<VerifiedIcon />}
                  />
                )}
              </Stack>
              <Stack
                direction="row"
                justifyContent="flex-start"
                alignItems="flex-start"
                spacing={2}
              >
                <Typography variant="subtitle1" color="textSecondary">
                  <strong>Created at:</strong>{' '}
                  {moment(data.created_at).format('L LTS')}
                </Typography>
                <Typography variant="subtitle1" color="textSecondary">
                  <strong>Uploaded by:</strong> {data.uploaded_by}
                </Typography>
              </Stack>
              <Box sx={{ m: 2 }}></Box>
              <Typography variant="h6">
                {data.release_name} - {data.product_type_name}
              </Typography>
              {data.description !== '' && (
                <Typography variant="body">{data.description}</Typography>
              )}
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper elevation={2} className={classes.paper}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                endIcon={<DownloadIcon />}
                href={data.main_file}
              >
                Download
              </Button>
              <Typography variant="body2" align="right" color="textSecondary">
                ({prettyBytes(Number(data.file_size))})
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
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
