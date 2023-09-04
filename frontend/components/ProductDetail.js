import ShareIcon from '@mui/icons-material/Share'
import VerifiedIcon from '@mui/icons-material/Verified'
import LoadingButton from '@mui/lab/LoadingButton'
import {
  Tabs,
  Tab,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Paper,
  Snackbar,
  Stack,
  Typography,
  CardMedia
} from '@mui/material'
import Alert from '@mui/material/Alert'
import ProductShare from './ProductShare'

import moment from 'moment'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'
import React from 'react'
import Loading from '../components/Loading'
import ProductDataGrid from '../components/ProductDataGrid'
import ProductNotFound from '../components/ProductNotFound'
import {
  downloadProduct,
  getProduct,
  getProductFiles,
  getProducts
} from '../services/product'
import useStyles from '../styles/pages/product'

export default function ProductDetail({ productId, internalName }) {
  const classes = useStyles()

  const [product, setProduct] = React.useState(null)
  const [files, setFiles] = React.useState([])
  const [isLoading, setLoading] = React.useState(false)
  const [notFound, setNotFound] = React.useState(false)
  const [isDownloading, setDownloading] = React.useState(false)
  const [shareDialogOpen, setShareDialogOpen] = React.useState(false)
  const [snackbarOpen, setSnackbarOpen] = React.useState(false)
  const productShareRef = React.useRef(null)

  const [activeTab, setActiveTab] = React.useState(0)
  const [hasHtmlFile, setHasHtmlFile] = React.useState(false)

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
        if (res.results.length === 0) {
          setNotFound(true)
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

        const hasHtmlFile = res.results.some(file =>
          file.name.toLowerCase().endsWith('.html')
        )
        setHasHtmlFile(hasHtmlFile)

        setActiveTab(hasHtmlFile ? 1 : 0)

        setLoading(false)

        return res.results
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
    const extension = file.name.split('.').pop()
    if (file.name.length > 30) {
      name = file.name.substring(0, 23) + '...' + extension
    }
    return (
      <ListItem key={`file_${file.id}`} disableGutters>
        {file.role === 0 && (
          <ListItemText
            primary={name}
            secondary={`Main file ${prettyBytes(file.size)}`}
            primaryTypographyProps={{
              noWrap: true
            }}
          />
        )}
        {file.role !== 0 && (
          <ListItemText
            primary={name}
            secondary={prettyBytes(file.size)}
            primaryTypographyProps={{
              noWrap: true
            }}
          />
        )}
      </ListItem>
    )
  }

  const handleShareDialogOpen = () => {
    setShareDialogOpen(!shareDialogOpen)
  }

  if (isLoading) return <Loading isLoading={isLoading} />
  if (notFound) return <ProductNotFound />
  if (!product) return null

  return (
    <React.Fragment>
      <Box className={classes.pageHeader}>
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={3000}
          onClose={() => setSnackbarOpen(false)}
        >
          <Alert
            onClose={() => setSnackbarOpen(false)}
            severity="success"
            sx={{ width: '100%' }}
          >
            Link copied successfully!
          </Alert>
        </Snackbar>
        <Typography variant="h6">Product</Typography>
      </Box>
      <Box component="form" noValidate autoComplete="off">
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
                justifyContent="flex-start"
                alignItems="center"
                spacing={2}
              >
                <Typography variant="h4">{product.display_name}</Typography>
                {product.status === 1 && (
                  <IconButton onClick={handleShareDialogOpen}>
                    <ShareIcon />
                  </IconButton>
                )}
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
                <Typography variant="body1">{product.description}</Typography>
              )}
              <ProductShare
                isOpen={shareDialogOpen}
                handleShareDialogOpen={handleShareDialogOpen}
                url={window.location.href}
                setParentSnackbarOpen={setSnackbarOpen}
                productShareRef={productShareRef}
              />
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper elevation={2} className={classes.paper}>
              <Stack divider={<Divider flexItem />} spacing={2}>
                {product.status === 1 && (
                  <LoadingButton
                    loading={isDownloading}
                    variant="contained"
                    onClick={downloadFile}
                  >
                    Download
                  </LoadingButton>
                )}
                <List>
                  {files.map(pc => {
                    return createFileFields(pc)
                  })}
                </List>
              </Stack>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent>
                <Tabs
                  value={activeTab}
                  onChange={(event, newValue) => setActiveTab(newValue)}
                >
                  {hasHtmlFile && <Tab label="Description File" value={1} />}
                  <Tab label="Table Preview" value={0} />
                </Tabs>
                {activeTab === 0 && <ProductDataGrid productId={product.id} />}
                {activeTab === 1 && hasHtmlFile && (
                  <div>
                    {files.map(file => {
                      if (file.name.toLowerCase().endsWith('.html')) {
                        return (
                          <CardMedia
                            component="iframe"
                            src={file.file}
                            height="800"
                            key={file.id}
                            sx={{ border: 'none' }}
                          />
                        )
                      }
                      return null
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </React.Fragment>
  )
}

ProductDetail.propTypes = {
  productId: PropTypes.number,
  internalName: PropTypes.string
}
