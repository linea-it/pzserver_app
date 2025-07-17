import CloseIcon from '@mui/icons-material/Close'
import UploadIcon from '@mui/icons-material/Upload'
import {
  Alert,
  Box,
  Button,
  FormGroup,
  Grid,
  Stack,
  TextField,
  Typography
} from '@mui/material'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import Link from '@mui/material/Link'
import prettyBytes from 'pretty-bytes'
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import {
  MAX_UPLOAD_SIZE,
  createProductFile,
  deleteProductFile,
  getProductFiles,
  registryProduct
} from '../../services/product'
import FileUploader from '../FileUploader'
import LinearProgressWithLabel from '../LinearProgressWithLabel'
import Loading from '../Loading'
export default function NewProductStep2({ productId, onNext, onPrev }) {
  const [mainFile, setMainFile] = useState(false)
  const [mainFileError, setMainFileError] = useState('')
  // const [descFile, setDescFile] = useState(false)
  // const [descFileError, setDescFileError] = useState('')
  const [files, setFiles] = useState([])
  const [auxFileError, setAuxFileError] = useState('')
  const [isLoading, setLoading] = useState(false)
  const [progress, setProgress] = useState(null)
  const [formError, setFormError] = React.useState('')

  const loadFiles = React.useCallback(async () => {
    setFormError('')
    setLoading(true)
    let hasMain = false
    // let hasDescription = false

    getProductFiles(productId)
      .then(res => {
        const files = res.results
        files.forEach(row => {
          if (row.role === 0) {
            hasMain = true
          }
          // if (row.role === 1) {
          //   hasDescription = true
          // }
        })
        setLoading(false)

        setMainFile(hasMain)
        // setDescFile(hasDescription)

        setFiles(files)
      })
      .catch(res => {
        if (res.response.status === 500) {
          // Tratamento erro no backend
          catchFormError(res.response.data)
        }
        setLoading(false)
      })
  }, [productId])

  useEffect(() => {
    loadFiles()
  }, [loadFiles])

  const handleNext = () => {
    setFormError('')
    setLoading(true)
    // Executa o registro das colunas do produto
    // Necessário para a associação.
    registryProduct(productId)
      .then(data => {
        setLoading(false)
        onNext(data.id)
      })
      .catch(res => {
        if (res.response.status === 500) {
          // Tratamento erro no backend
          catchFormError(res.response.data)
        }
        setLoading(false)
      })
  }
  const handlePrev = () => {
    onPrev(productId)
  }

  const handleRemoveFile = id => {
    // remove a mensagem de erro
    if (formError !== '') {
      setFormError('')
    }

    deleteProductFile(id)
      .then(() => {
        // Forcar um reload dos arquivos
        loadFiles(productId)
      })
      .catch(res => {
        if (res.response.status === 500) {
          // Tratamento erro no backend
          catchFormError(res.response.data)
        }
      })
  }

  const handleMouseDownPassword = event => {
    event.preventDefault()
  }

  const renderDisplayFile = file => {
    let label = ''
    switch (file.role) {
      case 0:
        label = 'Main File'
        break
      case 1:
        label = 'Description File'
        break
      case 2:
        label = 'Auxiliary File'
        break
    }

    return (
      <FormGroup row key={`display_file_${file.id}`}>
        <TextField
          value={file.name}
          label={label}
          readOnly
          fullWidth
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => handleRemoveFile(file.id)}
                  onMouseDown={handleMouseDownPassword}
                  edge="end"
                >
                  <CloseIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
          helperText={prettyBytes(Number(file.size))}
        />
      </FormGroup>
    )
  }

  const onProgress = progressEvent => {
    const progress = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    )
    setProgress(progress)
  }

  const handleFileError = (role, error) => {
    switch (role) {
      case 0:
        setMainFileError(error)
        break
      // case 1:
      //   setDescFileError(error)
      //   break
      default:
        setAuxFileError(error)
    }
  }
  const handleUploadFile = (file, role) => {
    // remove as mensagens de erro ao fazer um novo upload
    handleFileError(role, '')
    if (formError !== '') {
      setFormError('')
    }
    createProductFile(productId, file, role, onProgress)
      .then(res => {
        if (res.status === 201) {
          setProgress(null)
          // Forcar um reload dos arquivos
          loadFiles(productId)
        }
      })
      .catch(res => {
        if (res.response.status === 400) {
          // Tratamento erro no backend regra de negocio dos arquivos enviados
          handleFileError(role, res.response.data.error)
        }
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
        setProgress(null)
      })
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later, if the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  const handleFormError = () => {
    return (
      <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
        {formError}
      </Alert>
    )
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Typography paragraph variant="body1">
        Please select the file(s) for the upload. The main file is the one
        containing the data. It must be a single file. For example, if the
        product type is Redshift Sample or Training Set, the data must be
        tabular, and the tool supports the formats: CSV, FITS, HDF5, and
        Parquet. Otherwise, if the product type is, e.g., Training Results or
        Validation Results, the file format is free (in case of multiple files,
        please provide them compressed in a .zip or .tar file).
      </Typography>
      <Typography paragraph variant="body1">
        The maximum upload size is {MAX_UPLOAD_SIZE}MB. If your dataset is
        larger, please contact the Photo-z Server team to request an exception.
      </Typography>
      <Typography paragraph variant="body1">
        For text files, e.g., CSV, all commented lines are ignored. Index column
        and header are optional (multiline headers are ignored).
      </Typography>
      <Typography paragraph variant="body1">
        Note: If the files are meant to be used as input by the Photo-z Server
        Pipelines, there are additional requirements regarding the file
        contents. Please check out the{' '}
        <Link
          href="https://docs.linea.org.br/en/sci-platforms/pz_server.html"
          target="_blank"
          rel="noreferrer"
        >
          documentation page
        </Link>{' '}
        for more details.
      </Typography>
      {/* <Typography paragraph variant="body">
        The description file is supposed to contain relevant information about
        the data product. It can be a PDF document, a Jupyter notebook, etc.
      </Typography> */}
      <Typography paragraph variant="body1">
        The Auxiliary Files are in free format and can be multiple files (press
        the upload button as many times as necessary).
      </Typography>

      <Box>
        <Grid container spacing={4}>
          <Grid item xs={6}>
            <Box>
              <Stack spacing={2}>
                {mainFile === true && (
                  <Alert severity="success">Main File Uploaded!</Alert>
                )}
                {mainFile === false && (
                  <FileUploader
                    id="main_file"
                    onFileSelectSuccess={file => {
                      handleUploadFile(file, 0)
                    }}
                    onFileSelectError={e => {
                      handleFileError(0, e.error)
                    }}
                    maxSize={MAX_UPLOAD_SIZE} // 200 MB
                    buttonProps={{
                      color: 'primary',
                      disabled: progress !== null,
                      label: 'Choose Main File',
                      startIcon: <UploadIcon />,
                      fullWidth: true
                    }}
                  />
                )}
                {mainFileError !== '' && (
                  <Alert variant="outlined" severity="error">
                    {mainFileError}
                  </Alert>
                )}
              </Stack>
            </Box>
            {/* <Box sx={{ mt: 4 }}>
              <Stack spacing={2}>
                {descFile === true && (
                  <Alert severity="success">Description File Uploaded!</Alert>
                )}
                {descFile === false && (
                  <FileUploader
                    id="description_file"
                    onFileSelectSuccess={file => {
                      handleUploadFile(file, 1)
                    }}
                    onFileSelectError={e => {
                      handleFileError(1, e.error)
                    }}
                    maxSize={200} // 200 MB
                    buttonProps={{
                      color: 'primary',
                      disabled: progress !== null,
                      label: 'Choose Description File',
                      startIcon: <UploadIcon />,
                      fullWidth: true
                    }}
                  />
                )}
                {descFileError !== '' && (
                  <Alert variant="outlined" severity="error">
                    {descFileError}
                  </Alert>
                )}
              </Stack>
            </Box> */}
            <Box sx={{ mt: 4 }}>
              <Stack spacing={2}>
                <FileUploader
                  id="auxiliary_file"
                  onFileSelectSuccess={file => {
                    handleUploadFile(file, 2)
                  }}
                  onFileSelectError={e => {
                    handleFileError(2, e.error)
                  }}
                  maxSize={MAX_UPLOAD_SIZE} // 200 MB
                  buttonProps={{
                    startIcon: <UploadIcon />,
                    disabled: progress !== null,
                    fullWidth: true
                  }}
                />
                {auxFileError !== '' && (
                  <Alert variant="outlined" severity="error">
                    {auxFileError}
                  </Alert>
                )}
              </Stack>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box
              component="form"
              sx={{
                '& > :not(style)': { mb: 3 },
                pt: 2
              }}
              autoComplete="off"
            >
              {progress && (
                <Box>
                  <LinearProgressWithLabel value={progress} />
                </Box>
              )}
              {files.map(row => {
                return renderDisplayFile(row)
              })}
            </Box>
          </Grid>
        </Grid>
        {formError !== '' && handleFormError()}
        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            variant="contained"
            color="secondary"
            onClick={handlePrev}
            sx={{ mr: 1 }}
          >
            Prev
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={!mainFile}
          >
            Next
          </Button>
        </Box>
      </Box>
    </React.Fragment>
  )
}

NewProductStep2.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}
