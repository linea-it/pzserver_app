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

export default function NewProductStep4({ record, onNext, onPrev }) {
  const classes = useStyles()

  const [product, setProduct] = React.useState(record)
  const handleSubmit = e => {
    console.log('Step 4 Click')
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
          Finish
        </Button>
      </Box>
    </Box>
  )
}
