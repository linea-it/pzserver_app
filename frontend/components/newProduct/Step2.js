import React, { useState, useEffect } from 'react'
import {
  Grid,
  Typography,
  TextField,
  FormGroup,
  Button,
  Box,
  Backdrop
} from '@mui/material'
import FileUploader from '../FileUploader'
import useStyles from '../../styles/pages/newproduct'
import Loading from '../Loading'
import LinearProgressWithLabel from '../LinearProgressWithLabel'
import {
  getProductFiles,
  deleteProductFile,
  createProductFile
} from '../../services/product'
import InputAdornment from '@mui/material/InputAdornment'
import CloseIcon from '@mui/icons-material/Close'
import UploadIcon from '@mui/icons-material/Upload'
import CheckIcon from '@mui/icons-material/Check'
import IconButton from '@mui/material/IconButton'

export default function NewProductStep2({ record, onNext, onPrev }) {
  const classes = useStyles()

  const [product, setProduct] = useState(record)
  const [mainFile, setMainFile] = useState(false)
  const [descFile, setDescFile] = useState(false)
  const [files, setFiles] = useState([])
  const [isLoading, setLoading] = useState(false)
  const [progress, setProgress] = useState(null)

  const handleSubmit = e => {
    console.log('Step 2 Click')
    onNext(product)
  }

  const loadFiles = productId => {
    setLoading(true)
    let hasMain = false
    let hasDescription = false

    getProductFiles(productId)
      .then(res => {
        const files = res.results
        files.forEach(row => {
          if (row.role === 0) {
            hasMain = true
          }
          if (row.role === 1) {
            hasDescription = true
          }
        })

        setMainFile(hasMain)
        setDescFile(hasDescription)

        setFiles(files)

        setLoading(false)
      })
      .catch(res => {
        // Retorna error
        // TODO: Tratar os errors e apresentar.
        setLoading(false)
      })
  }

  useEffect(() => {
    loadFiles(product.id)
  }, [product])

  const handleRemoveFile = id => {
    console.log('Remove Main File: %o', id)

    deleteProductFile(id)
      .then(res => {
        console.log(res)
        // Forcar um reload dos arquivos
        loadFiles()
      })
      .catch(res => {
        console.log(res)
        // TODO: Tratar error ao deletar um arquivo
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
                  onClick={e => handleRemoveFile(file.id)}
                  onMouseDown={handleMouseDownPassword}
                  edge="end"
                >
                  <CloseIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </FormGroup>
    )
  }

  const onProgress = progressEvent => {
    console.log('progressEvent')
    const progress = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    )
    setProgress(progress)
  }

  const handleUploadFile = (file, role) => {
    console.log('File: %o, Role: %o', file, role)
    setLoading(true)
    createProductFile(product.id, file, role, onProgress)
      .then(res => {
        if (res.status === 201) {
          setLoading(false)
          const data = res.data
          console.log(data)

          setProgress(null)
          // Forcar um reload dos arquivos
          loadFiles()
        }
      })
      .catch(res => {
        // TODO: Exibir mensagem de error
        console.log('Error!')
        console.log(res.response.data)
        setProgress(null)
        setLoading(false)
      })
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Box
        sx={{
          '& > :not(style)': { m: 1 }
        }}
        autoComplete="off"
      >
        <Grid container>
          <Grid item xs={6}>
            <Box>
              <Typography variant="body">
                Main File Lorem ipsum dolor sit amet, consectetur adipiscing
                elit
              </Typography>
              <FileUploader
                id="main_file"
                onFileSelectSuccess={file => {
                  handleUploadFile(file, 0)
                }}
                onFileSelectError={e => {
                  console.log(e)
                }}
                maxSize={200} // 200 MB
                buttonProps={{
                  color: mainFile ? 'success' : 'primary',
                  // disabled: mainFile
                  label: mainFile ? 'Main File Uploaded' : 'Choose Main File',
                  startIcon: mainFile ? <CheckIcon /> : <UploadIcon />
                }}
              />
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body">
                Description File Lorem ipsum dolor sit amet, consectetur
                adipiscing elit
              </Typography>
              <FileUploader
                id="description_file"
                onFileSelectSuccess={file => {
                  handleUploadFile(file, 1)
                }}
                onFileSelectError={e => {
                  console.log(e)
                }}
                maxSize={200} // 200 MB
                buttonProps={{
                  color: descFile ? 'success' : 'primary',
                  label: descFile
                    ? 'Description File Uploaded'
                    : 'Choose Description File',
                  startIcon: descFile ? <CheckIcon /> : <UploadIcon />
                }}
              />
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body">
                Auxiliary Files Lorem ipsum dolor sit amet, consectetur
                adipiscing elit
              </Typography>
              <FileUploader
                id="auxiliary_file"
                onFileSelectSuccess={file => {
                  handleUploadFile(file, 2)
                }}
                onFileSelectError={e => {
                  console.log(e)
                }}
                maxSize={200} // 200 MB
                buttonProps={{
                  startIcon: <UploadIcon />
                }}
              />
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box
              component="form"
              sx={{
                '& > :not(style)': { m: 2 }
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

        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            variant="contained"
            color="secondary"
            onClick={onPrev}
            sx={{ mr: 1 }}
          >
            Prev
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          <Button
            // type="submit"
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={!mainFile}
          >
            Next
          </Button>
        </Box>
      </Box>
    </React.Fragment>
  )
}
