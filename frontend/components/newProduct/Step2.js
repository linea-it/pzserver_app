import React from 'react'
import {
  Container,
  Grid,
  Typography,
  TextField,
  Checkbox,
  FormGroup,
  FormControl,
  FormControlLabel,
  Button,
  Box
} from '@mui/material'
import ProductTypeSelect from '../ProductTypeSelect'
import ReleaseSelect from '../ReleaseSelect'
import FileUploader from '../FileUploader'
import useStyles from '../../styles/pages/newproduct'

export default function NewProductStep2({ record, onNext, onPrev }) {
  const classes = useStyles()

  const [product, setProduct] = React.useState(record)
  const handleSubmit = e => {
    console.log('Step 2 Click')
    onNext(product)
  }

  return (
    <Box
      component="form"
      sx={{
        '& > :not(style)': { m: 1 }
      }}
      autoComplete="off"
    // onSubmit={handleSubmit}
    >
      <FormGroup row>
        <TextField
          name="main_file"
          value={product.main_file ? product.main_file.name : ''}
          label="Main File"
          readOnly
          required
        />
        <FileUploader
          id="main_file"
          onFileSelectSuccess={file => {
            setProduct({
              ...product,
              main_file: file
            })
          }}
          onFileSelectError={e => {
            console.log(e)
          }}
          maxSize={200} // 200 MB
        />
      </FormGroup>

      <FormGroup row>
        <TextField
          name="main_file"
          value={product.description_file ? product.description_file.name : ''}
          label="Description File"
          readOnly
          required
        />
        <FileUploader
          id="description_file"
          onFileSelectSuccess={file => {
            setProduct({
              ...product,
              description_file: file
            })
          }}
          onFileSelectError={e => {
            console.log(e)
          }}
          maxSize={200} // 200 MB
        />
      </FormGroup>
      <Button variant="contained" sx={{ mr: 1 }}>
        Add more files
      </Button>

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
        >
          Next
        </Button>
      </Box>
    </Box>
  )
}
