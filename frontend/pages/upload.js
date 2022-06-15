import React, { useRef } from 'react'
import {
  Container,
  Grid,
  Typography,
  TextField,
  Input,
  MenuItem,
  FormGroup,
  Button,
  Box
} from '@mui/material'
import InputLabel from '@mui/material/InputLabel'
import ProductTypeSelect from '../components/ProductTypeSelect'
import ReleaseSelect from '../components/ReleaseSelect'
import FormControl from '@mui/material/FormControl'
import useStyles from '../styles/pages/upload'
import { parseCookies } from 'nookies'
import FileUploader from '../components/FileUploader'
import { createProduct } from '../services/product'
import { uniqueId } from 'lodash'

export default function Upload() {
  const classes = useStyles()

  //   {
  //     "id": 8,
  //     "release": 2,
  //     "release_name": "LSST DP1",
  //     "product_type": 4,
  //     "product_type_name": "Training Sets",
  //     "uploaded_by": "gverde",
  //     "display_name": "Produto 8",
  //     "main_file": "http://localhost/archive/data/BluejeansHelper_A5J4FIm.log",
  //     "file_name": "BluejeansHelper",
  //     "file_size": 13176,
  //     "file_extension": ".log",
  //     "description_file": "http://localhost/archive/data/BluejeansHelper_lnM9OvZ.log",
  //     "official_product": true,
  //     "survey": "",
  //     "pz_code": "",
  //     "description": "",
  //     "created_at": "2022-05-19T20:02:02.690868Z"
  // }
  const [progress, setProgress] = React.useState(0)
  const [product, setProduct] = React.useState({
    display_name: 'teste_' + uniqueId(),
    release: '1',
    product_type: '1',
    official_product: true,
    main_file: null,
    description_file: '',
    survey: '',
    pz_code: '',
    description: ''
  })

  const onUploadProgress = e => {
    const a = Math.round((100 * e.loaded) / e.total)
    console.log('onUploadProgress: %o', a)
    setProgress(Math.round((100 * e.loaded) / e.total))
  }

  const handleSubmit = e => {
    e.preventDefault()
    console.log('Submit')
    console.log(product)

    createProduct(product, onUploadProgress).then(res => {
      console.log(res)

      // TODO: isso é só para teste
      setProduct({ ...product, display_name: 'teste_' + uniqueId() })
    })
  }

  return (
    <Container className={classes.container}>
      <Grid container spacing={2} className={classes.gridContainer}>
        <Grid item xs={12}>
          <Typography variant="h2" component="h1" align="center">
            Upload
          </Typography>
          <Box
            component="form"
            sx={{
              '& > :not(style)': { m: 1 }
            }}
            autoComplete="off"
            onSubmit={handleSubmit}
          >
            <FormControl fullWidth>
              <TextField
                id="name"
                value={product.display_name}
                label="Product Name"
                required
                onChange={e => {
                  setProduct({
                    ...product,
                    display_name: e.target.value
                  })
                }}
              />
            </FormControl>
            <FormControl fullWidth>
              <InputLabel id="release-select-label">Release</InputLabel>
              <ReleaseSelect
                labelId="release-select-label"
                value={product.release}
                onChange={value => {
                  setProduct({
                    ...product,
                    release: value
                  })
                }}
              />
            </FormControl>
            <FormControl fullWidth>
              <InputLabel id="producttype-select-label">
                Product Type
              </InputLabel>
              <ProductTypeSelect
                labelId="producttype-select-label"
                value={product.product_type}
                onChange={value => {
                  setProduct({
                    ...product,
                    product_type: value
                  })
                }}
              />
            </FormControl>
            <FormGroup row>
              <TextField
                value={product.main_file ? product.main_file.name : ''}
                label="Main File"
                readOnly
              />
              <FileUploader
                id="main_file"
                onFileSelectSuccess={file => {
                  setProduct({
                    ...product,
                    main_file: file
                    // description_file: file
                  })
                }}
                onFileSelectError={e => {
                  console.log(e)
                }}
                maxSize={200} // 200 MB
              />
            </FormGroup>
            {/* <FormControl fullWidth>
              <label htmlFor="main_file">
                <Input
                  id="main_file"
                  accept="image/*"
                  type="file"
                  label="Main File"
                  sx={{ display: 'none' }}
                  onChange={handleFileInput}
                />
                <Button variant="contained" component="span">
                  Upload
                </Button>
              </label>
            </FormControl> */}
            <FormControl fullWidth>
              <TextField
                id="description"
                value={product.description}
                label="Description"
                multiline
                minRows={8}
              />
            </FormControl>

            <Grid item xs={12} className={classes.buttonsContainer}>
              <Button type="reset" variant="contained" color="secondary">
                Clear Form
              </Button>
              <Button type="submit" variant="contained" color="primary">
                Submit
              </Button>
            </Grid>
          </Box>
        </Grid>
      </Grid>
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
