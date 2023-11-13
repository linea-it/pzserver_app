import UploadIcon from '@mui/icons-material/Upload'
import VerifiedIcon from '@mui/icons-material/Verified'

import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardActions from '@mui/material/CardActions'
import CardContent from '@mui/material/CardContent'
import Chip from '@mui/material/Chip'
import Container from '@mui/material/Container'
import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
import Snackbar from '@mui/material/Snackbar'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import moment from 'moment'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import React, { useState } from 'react'
import FileUploader from '../../../components/FileUploader'
import LinearProgressWithLabel from '../../../components/LinearProgressWithLabel'
import Loading from '../../../components/Loading'
import ProductFileTextField from '../../../components/ProductFileTextField'
import {
  MAX_UPLOAD_SIZE,
  createProductFile,
  getProductByInternalName,
  getProductFiles,
  patchProduct
} from '../../../services/product'

export default function EditProduct() {
  const router = useRouter()
  const { pid } = router.query

  const [isOpen, setIsOpen] = React.useState(false)
  const [originalProduct, setOriginalProduct] = React.useState(undefined)
  const [product, setProduct] = React.useState(undefined)
  const [files, setFiles] = React.useState([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [fileError, setFileError] = React.useState(undefined)
  const [progress, setProgress] = useState(null)

  const loadFiles = React.useCallback(async () => {
    setIsLoading(true)
    getProductFiles(product.id)
      .then(res => {
        setFiles(res.results)
        setIsLoading(false)
      })
      .catch(res => {
        if (res.response.status === 500) {
          // TODO: Tratamento erro no backend
        }
        setIsLoading(false)
      })
  }, [product])

  const loadProduct = React.useCallback(async () => {
    setIsLoading(true)
    getProductByInternalName(pid)
      .then(res => {
        // Apresenta a interface de Produtos
        setOriginalProduct(res)
        setProduct(res)
        setIsLoading(false)
      })
      .catch(res => {
        // Retorna error 404
        // TODO: Tratar os errors e apresentar.
        setIsLoading(false)
      })
  }, [pid])

  React.useEffect(() => {
    if (pid) {
      loadProduct()
    }
  }, [pid, loadProduct])

  React.useEffect(() => {
    if (product) {
      loadFiles()
    }
  }, [product, loadFiles])

  const handleUpdate = () => {
    patchProduct(product)
      .then(res => {
        if (res.status === 200) {
          setIsLoading(false)
          const data = res.data
          setProduct(data)
          setOriginalProduct(data)
          setIsOpen(true)
        }
      })
      .catch(res => {
        if (res.response.status === 400) {
          // Tratamento para erro nos campos
          // handleFieldsErrors(res.response.data)
        }
        if (res.response.status === 500) {
          // Tratamento erro no backend
          // catchFormError(res.response.data)
        }
        setIsLoading(false)
      })
  }

  const handleOnDeleteFile = fileId => {
    loadFiles()
  }

  const renderDisplayFile = file => {
    return (
      <ProductFileTextField
        key={`file_field_${file.id}`}
        id={file.id}
        role={file.role}
        name={file.name}
        size={file.size}
        readOnly={file.role === 0}
        onDelete={handleOnDeleteFile}
      />
    )
  }

  const onProgress = progressEvent => {
    const progress = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    )
    setProgress(progress)
  }

  const checkFileName = (name, files) => {
    let isOk = true
    // Verifica se já existe um arquivo com mesmo nome.
    files.forEach(f => {
      if (f.name === name) {
        isOk = false
      }
    })
    return isOk
  }

  const handleUploadFile = file => {
    // Os arquivos uploaded nesta página sempre serão auxiliares
    const role = 2

    if (!checkFileName(file.name, files)) {
      setFileError('A file with the same name already exists')
      return
    }

    createProductFile(product.id, file, role, onProgress)
      .then(res => {
        if (res.status === 201) {
          setProgress(null)
          loadFiles()
        }
      })
      .catch(res => {
        if (res.response.status === 400) {
          // Tratamento erro no backend regra de negocio dos arquivos enviados
          if ('file' in res.response.data) {
            setFileError(res.response.data.file[0])
          } else {
            setFileError(res.response.data.error)
          }
        }
        if (res.response.status === 500) {
          // catchFormError(res.response.data)
          setFileError(res.response.data.error)
        }
        setProgress(null)
        loadFiles()
      })
  }

  return (
    <Container sx={{ flex: 1, m: 4 }}>
      {isLoading && <Loading isLoading={isLoading} />}
      <React.Fragment>
        <Box mb={5}>
          <Typography variant="h6">Edit Product</Typography>
        </Box>
        <Box
          sx={{
            mt: 2,
            mb: 2,
            p: 2
          }}
          // height="400px"
          alignItems="center"
          justifyContent="center"
        >
          {product !== undefined && (
            <Grid
              container
              spacing={3}
              direction="row"
              justifyContent="flex-start"
              alignItems="stretch"
            >
              <Grid item xs={12}>
                <Card elevation={2}>
                  <CardContent>
                    <Stack
                      direction="row"
                      justifyContent="flex-start"
                      alignItems="center"
                      spacing={2}
                    >
                      <Typography variant="h4">
                        {product.display_name}
                      </Typography>
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
                    <Typography variant="body2">
                      Last update: {moment(product?.updated_at).format('L LTS')}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h6">
                        {product.release_name} - {product.product_type_name}
                      </Typography>

                      <FormControl sx={{ mt: 2 }} fullWidth>
                        <TextField
                          name="description"
                          value={product.description}
                          label="Description"
                          multiline
                          minRows={6}
                          onChange={e =>
                            setProduct(prev => {
                              return {
                                ...prev,
                                description: e.target.value
                              }
                            })
                          }
                          // onBlur={handleInputValue}
                          // error={!!fieldErrors.description}
                          // helperText={fieldErrors.description}
                        />
                      </FormControl>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      disabled={
                        originalProduct?.description === product?.description
                      }
                      onClick={handleUpdate}
                    >
                      Update
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Card elevation={2}>
                  <CardContent>
                    <Stack spacing={2}>
                      {files.map(row => {
                        return renderDisplayFile(row)
                      })}
                    </Stack>
                    {progress && <LinearProgressWithLabel value={progress} />}
                    <Stack spacing={2}>
                      <FileUploader
                        id="auxiliary_file"
                        onFileSelectSuccess={file => {
                          handleUploadFile(file)
                        }}
                        onFileSelectError={e => {
                          setFileError(e.error)
                        }}
                        maxSize={MAX_UPLOAD_SIZE} // 200 MB
                        buttonProps={{
                          startIcon: <UploadIcon />,
                          disabled: progress !== null,
                          fullWidth: true
                        }}
                      />
                      {fileError !== undefined && (
                        <Alert
                          variant="outlined"
                          severity="error"
                          onClose={() => {
                            setFileError(undefined)
                          }}
                        >
                          {fileError}
                        </Alert>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
        <Snackbar
          open={isOpen}
          autoHideDuration={6000}
          onClose={() => setIsOpen(false)}
          message="Product has been updated"
        />
      </React.Fragment>
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
