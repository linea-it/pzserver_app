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
import ProductTypeSelect from '../../components/ProductTypeSelect'
import ReleaseSelect from '../../components/ReleaseSelect'
import FileUploader from '../../components/FileUploader'
import useStyles from '../../styles/pages/newproduct'

export default function NewProductStep1({ record, onNext, onPrev }) {
  const classes = useStyles()

  const [product, setProduct] = React.useState(record)
  const handleSubmit = e => {
    console.log('Step 1 First Click')
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
      <FormControl fullWidth>
        <TextField
          id="display_name"
          name="display_name"
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
        <ProductTypeSelect
          value={product.product_type}
          onChange={value => {
            setProduct({
              ...product,
              product_type: value
            })
          }}
          required
        />
      </FormControl>
      <FormControl fullWidth>
        <ReleaseSelect
          value={product.release}
          onChange={value => {
            setProduct({
              ...product,
              release: value
            })
          }}
        />
      </FormControl>
      {/* Survey necessário Product Type = 2 - Spec-z Catalog */}
      {product.product_type === 2 && (
        <FormControl fullWidth>
          <TextField
            id="survey"
            name="survey"
            value={product.survey}
            label="Survey"
            onChange={e => {
              setProduct({
                ...product,
                survey: e.target.value
              })
            }}
          />
        </FormControl>
      )}
      {/* Survey necessário Product Type = 1 - Photo-z Results */}
      {product.product_type === 1 && (
        <FormControl fullWidth>
          <TextField
            id="pz_code"
            name="pz_code"
            value={product.pz_code}
            label="Pz Code"
            onChange={e => {
              setProduct({
                ...product,
                pz_code: e.target.value
              })
            }}
          />
        </FormControl>
      )}
      <FormControl fullWidth>
        <FormControlLabel
          control={
            <Checkbox
              name="official_product"
              checked={product.official_product}
              onChange={e => {
                setProduct({
                  ...product,
                  official_product: e.target.checked
                })
              }}
            />
          }
          label="Official Product"
        />
      </FormControl>
      <FormControl fullWidth>
        <TextField
          id="description"
          name="description"
          value={product.description}
          label="Description"
          multiline
          minRows={8}
          onChange={e => {
            setProduct({
              ...product,
              description: e.target.value
            })
          }}
          required
        />
      </FormControl>
      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Box sx={{ flex: '1 1 auto' }} />
        {/* <Button
          type="reset"
          value="reset"
          variant="contained"
          color="secondary"
          // onClick={handleReset}
          sx={{ mr: 1 }}
        >
          Clear Form
        </Button> */}
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
