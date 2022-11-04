import React from 'react'
import useStyles from '../styles/pages/product'
import {
  Grid,
  Typography,
  Paper,
  Box,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider
} from '@mui/material'
import LoadingButton from '@mui/lab/LoadingButton'
import Link from '../components/Link'
import VerifiedIcon from '@mui/icons-material/Verified'
import {
  downloadProduct,
  getProductFiles,
  getProduct,
  getProducts
} from '../services/product'
import moment from 'moment'
import prettyBytes from 'pretty-bytes'
import Loading from '../components/Loading'
import DefaultErrorPage from 'next/error'
import PropTypes from 'prop-types'
import DownloadIcon from '@mui/icons-material/Download'

export default function ProductDetail({ productId, internalName }) {
  const classes = useStyles()

  const [product, setProduct] = React.useState(null)
  const [files, setFiles] = React.useState([])
  const [isLoading, setLoading] = React.useState(false)
  const [notFound, setNotFound] = React.useState(false)
  const [isDownloading, setDownloading] = React.useState(false)

  const loadProductById = React.useCallback(async () => {
    setLoading(true)
    getProduct(productId)
      .then(res => {
        setProduct(res)
        setLoading(false)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          // TODO: Tratar erro
          setNotFound(true)
        }
      })
  }, [productId])

  React.useEffect(() => {
    if (productId) {
      loadProductById()
    }
  }, [loadProductById, productId])

  const loadProductByName = React.useCallback(async () => {
    setLoading(true)
    getProducts({ filters: { internal_name: internalName } })
      .then(res => {
        // Apresenta a interface de Produtos
        if (res.results.length === 1) {
          setLoading(false)
          setProduct(res)
        }
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          // TODO: Tratar erro
          setNotFound(true)
        }
      })

    getProducts({ filters: { internal_name: internalName } })
      .then(res => {
        // Apresenta a interface de Produtos
        if (res.results.length === 1) {
          setProduct(res.results[0])
        }
        setLoading(false)
      })
      .catch(res => {
        // Retorna error 404
        // TODO: Tratar os errors e apresentar.
        setLoading(false)
      })
  }, [internalName])

  React.useEffect(() => {
    if (internalName) {
      loadProductByName()
    }
  }, [loadProductByName, internalName])

  const loadFiles = React.useCallback(async () => {
    if (!product.id) {
      return
    }
    setLoading(true)

    getProductFiles(product.id)
      .then(res => {
        setFiles(res.results)

        setLoading(false)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          // TODO: Tratar erro
        }
      })
  }, [product])

  React.useEffect(() => {
    if (product) {
      loadFiles()
    }
  }, [loadFiles, product])

  const downloadFile = () => {
    setDownloading(true)
    downloadProduct(product.id, product.internal_name)
      .then(res => {
        const link = document.createElement('a')
        link.target = '_blank'
        link.download = product.internal_name
        link.href = URL.createObjectURL(
          new Blob([res.data], { type: res.headers['content-type'] })
        )
        link.click()
        setDownloading(false)
      })
      .catch(() => {
        // TODO: Tratar erro no download
        setDownloading(false)
      })
  }

  const createFileFields = file => {
    // Se o nome do arquivo for grande,
    // exibe só os primeiros caracteres + extensao.
    let name = file.name
    if (file.name.length > 30) {
      name = file.name.substring(0, 26) + file.name.slice(-4)
    }
    return (
      <ListItem
        key={`file_${file.id}`}
        disableGutters
        secondaryAction={
          <IconButton component={Link} href={file.file} target="_blank">
            <DownloadIcon />
          </IconButton>
        }
      >
        {file.role === 0 && (
          <ListItemText
            primary={name}
            secondary={`Main file ${prettyBytes(file.size)}`}
          />
        )}
        {file.role !== 0 && (
          <ListItemText primary={name} secondary={prettyBytes(file.size)} />
        )}
      </ListItem>
    )
  }

  if (isLoading) return <Loading isLoading={isLoading} />
  if (notFound) return <DefaultErrorPage statusCode={404} />
  if (!product) return null

  return (
    <React.Fragment>
      <Grid
        container
        spacing={3}
        direction="row"
        justifyContent="flex-start"
        alignItems="stretch"
      >
        <Grid item xs={8}>
          <Paper elevation={2} className={classes.paper}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="flex-start"
              spacing={2}
            >
              <Typography variant="h4">{product.display_name}</Typography>

              {product.official_product === true && (
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
                {moment(product.created_at).format('L LTS')}
              </Typography>
              <Typography variant="subtitle1" color="textSecondary">
                <strong>Uploaded by:</strong> {product.uploaded_by}
              </Typography>
            </Stack>
            <Box sx={{ m: 2 }}></Box>
            <Typography variant="h6">
              {product.release_name} - {product.product_type_name}
            </Typography>
            {product.description !== '' && (
              <Typography variant="body">{product.description}</Typography>
            )}
          </Paper>
        </Grid>
        <Grid item xs={4}>
          <Paper elevation={2} className={classes.paper}>
            <Stack divider={<Divider flexItem />} spacing={2}>
              <LoadingButton
                loading={isDownloading}
                variant="contained"
                onClick={downloadFile}
              >
                Download
              </LoadingButton>
              <List>
                {files.map(pc => {
                  return createFileFields(pc)
                })}
              </List>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </React.Fragment>
  )
}

ProductDetail.propTypes = {
  productId: PropTypes.number,
  internalName: PropTypes.string
}
