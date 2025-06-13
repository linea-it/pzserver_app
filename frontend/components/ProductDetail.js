import React from 'react'

import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'
import EditIcon from '@mui/icons-material/Edit'
import ShareIcon from '@mui/icons-material/Share'
import VerifiedIcon from '@mui/icons-material/Verified'

import LoadingButton from '@mui/lab/LoadingButton'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Breadcrumbs from '@mui/material/Breadcrumbs'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardMedia from '@mui/material/CardMedia'
import Chip from '@mui/material/Chip'
import Divider from '@mui/material/Divider'
import Grid from '@mui/material/Grid'
import IconButton from '@mui/material/IconButton'
import Link from '@mui/material/Link'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Paper from '@mui/material/Paper'
import Snackbar from '@mui/material/Snackbar'
import Stack from '@mui/material/Stack'
import Tab from '@mui/material/Tab'
import Tabs from '@mui/material/Tabs'
import Tooltip from '@mui/material/Tooltip'
import Typography from '@mui/material/Typography'
import moment from 'moment'
import { useRouter } from 'next/router'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'
import Loading from '../components/Loading'
import ProductDataGrid from '../components/ProductDataGrid'
import ProductNotFound from '../components/ProductNotFound'
import { getProcessByUpload } from '../services/process'
import {
  downloadProduct,
  getProduct,
  getProductFiles,
  getProducts
} from '../services/product'
import useStyles from '../styles/pages/product'
import ProductShare from './ProductShare'
export default function ProductDetail({ productId, internalName }) {
  const router = useRouter()
  const classes = useStyles()

  const [product, setProduct] = React.useState(null)
  const [process, setProcess] = React.useState(null)
  const [files, setFiles] = React.useState([])
  const [isLoading, setLoading] = React.useState(false)
  const [notFound, setNotFound] = React.useState(false)
  const [isDownloading, setDownloading] = React.useState(false)
  const [shareDialogOpen, setShareDialogOpen] = React.useState(false)
  const [snackbarOpen, setSnackbarOpen] = React.useState(false)
  const productShareRef = React.useRef(null)

  const [activeTab, setActiveTab] = React.useState(0)
  const [hasHtmlFile, setHasHtmlFile] = React.useState(false)
  const [isTabular, setIsTabular] = React.useState(false)

  const loadProductById = React.useCallback(async () => {
    setLoading(true)
    getProduct(productId)
      .then(res => {
        setProduct(res)
        setLoading(false)
      })
      .catch(error => {
        setLoading(false)
        if (error.response && error.response.status === 500) {
          console.error('Internal Server Error:', error.response.data)
        } else {
          console.error('Error loading product by ID:', error.message)
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

    try {
      const res = await getProducts({
        filters: { internal_name: internalName }
      })

      if (res.results.length === 1) {
        setLoading(false)
        setProduct(res.results[0])
      } else if (res.results.length === 0) {
        setLoading(false)
        setNotFound(true)
      }
    } catch (error) {
      setLoading(false)

      if (error.response && error.response.status === 404) {
        console.error('Product not found:', error.response.data)
      } else if (error.response && error.response.status === 500) {
        console.error('Internal Server Error:', error.response.data)
      } else {
        console.error('Error loading product by name:', error.message)
      }
    }
  }, [internalName])

  React.useEffect(() => {
    if (internalName) {
      loadProductByName()
    }
  }, [loadProductByName, internalName])

  const loadProcessByUpload = React.useCallback(async () => {
    if (!product.id) {
      return
    }
    setLoading(true)
    getProcessByUpload(product.id)
      .then(res => {
        console.log('res', res)
        setProcess(res)
        setLoading(false)
      })
      .catch(error => {
        setLoading(false)
        if (error.response && error.response.status === 500) {
          console.error('Internal Server Error:', error.response.data)
        } else {
          console.error('Error loading process by ID:', error.message)
        }
      })
  }, [product])

  React.useEffect(() => {
    if (product) {
      loadProcessByUpload()
    }
  }, [loadProcessByUpload, product])

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

        const isTabularData = res.results.some(file => {
          const lowerName = file.name.toLowerCase()
          return (
            lowerName.endsWith('.csv') ||
            lowerName.endsWith('.xls') ||
            lowerName.endsWith('.xlsx') ||
            lowerName.endsWith('.txt') ||
            lowerName.endsWith('.fit') ||
            lowerName.endsWith('.fits') ||
            lowerName.endsWith('.h5') ||
            lowerName.endsWith('.hf5') ||
            lowerName.endsWith('.hdf') ||
            lowerName.endsWith('.hdf5') ||
            lowerName.endsWith('.pq') ||
            lowerName.endsWith('.parq') ||
            lowerName.endsWith('.parquet')
          )
        })
        setIsTabular(isTabularData)

        setLoading(false)

        return res.results
      })
      .catch(error => {
        setLoading(false)
        if (error.response && error.response.status === 500) {
          console.error('Internal Server Error:', error.response.data)
        } else {
          console.error('Error loading product files:', error.message)
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
      .catch(error => {
        console.error('Error downloading file:', error.message)
        setDownloading(false)
      })
  }

  const handleEdit = row => {
    router.push(`/product/edit/${product.internal_name}`)
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
            secondary={
              <>
                Main file {prettyBytes(file.size)}
                <br />
                Total of rows: {file.n_rows ? file.n_rows : 'undefined'}
              </>
            }
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
        <Breadcrumbs aria-label="breadcrumb">
          <Link color="inherit" href="/">
            Home
          </Link>
          <Typography>Data Products</Typography>
          <Typography color="textPrimary">Product</Typography>
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
                const returnPath = product.official_product
                  ? '/oficial_products'
                  : '/user_products'
                router.push(returnPath)
              }}
              color="primary"
              cursor="pointer"
            />
            <Typography variant="h6">Product</Typography>
          </Stack>
        </Box>
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
                {product.can_update === true && (
                  <IconButton onClick={handleEdit}>
                    <EditIcon />
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
                  <strong>Owner:</strong> {product.uploaded_by}
                </Typography>
                <Typography variant="subtitle1" color="textSecondary">
                  <strong>Origin:</strong> {product.origin}
                </Typography>
              </Stack>
              <Box sx={{ m: 2 }}></Box>
              <Stack
                direction="row"
                justifyContent="flex-start"
                alignItems="flex-start"
                spacing={2}
              >
                {product.release !== null && (
                  <Typography variant="subtitle1" color="textSecondary">
                    <strong>Release:</strong> {product.release_name}
                  </Typography>
                )}
                {process !== null && (
                  <>
                    <Typography variant="subtitle1" color="textSecondary">
                      <strong>
                        Source{process.provenance_inputs.length !== 1 && 's'}:
                      </strong>
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                      <List
                        sx={{
                          width: '100%',
                          maxWidth: 360,
                          bgcolor: 'background.paper',
                          position: 'relative',
                          overflow: 'auto',
                          maxHeight: 150,
                          '& ul': { padding: 0 }
                        }}
                        subheader={<li />}
                      >
                        {process.provenance_inputs.map(provInput => (
                          <ListItem
                            key={`section-${provInput.id}`}
                            component="div"
                            disablePadding
                          >
                            <ListItemButton>
                              <Tooltip
                                title={
                                  provInput.description ||
                                  'No description available'
                                }
                              >
                                <Link
                                  component="button"
                                  onClick={() => {
                                    setProduct(null)
                                    router.push(
                                      `/product/${provInput.internal_name}`
                                    )
                                  }}
                                >
                                  {provInput.display_name}
                                </Link>
                              </Tooltip>
                            </ListItemButton>
                          </ListItem>
                        ))}
                      </List>
                    </Typography>
                  </>
                )}
              </Stack>
              <Box sx={{ m: 2 }}></Box>
              {product.release !== null && (
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
                  <>
                    <LoadingButton
                      loading={isDownloading}
                      variant="contained"
                      onClick={downloadFile}
                    >
                      Download
                    </LoadingButton>
                    {isDownloading && (
                      <Alert variant="outlined" severity="info">
                        The files with data and metadata are being prepared for
                        the transfer. The download will begin shortly.
                      </Alert>
                    )}
                  </>
                )}
                <List>
                  {files.map(pc => {
                    return createFileFields(pc)
                  })}
                </List>
              </Stack>
            </Paper>
          </Grid>
          {isTabular && (
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
                  {activeTab === 0 && (
                    <ProductDataGrid productId={product.id} />
                  )}
                  {activeTab === 1 && hasHtmlFile && (
                    <Box>
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
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    </React.Fragment>
  )
}
ProductDetail.propTypes = {
  productId: PropTypes.number,
  internalName: PropTypes.string
}
