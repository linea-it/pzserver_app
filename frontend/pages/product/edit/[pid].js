import VerifiedIcon from '@mui/icons-material/Verified'
import {
  Container,
  Typography
} from '@mui/material'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardActions from '@mui/material/CardActions'
import CardContent from '@mui/material/CardContent'

import FormControl from '@mui/material/FormControl'
import Grid from '@mui/material/Grid'
import Snackbar from '@mui/material/Snackbar'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import moment from 'moment'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import React from 'react'
import Loading from '../../../components/Loading'
import { getProductByInternalName, patchProduct } from '../../../services/product'
import useStyles from '../../../styles/pages/newproduct'
export default function EditProduct() {
  const classes = useStyles()
  const router = useRouter()
  const { pid } = router.query

  const [isOpen, setIsOpen] = React.useState(false)
  const [originalProduct, setOriginalProduct] = React.useState(undefined)
  const [product, setProduct] = React.useState(undefined)
  const [isLoading, setIsLoading] = React.useState(false)


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
  }, [pid])

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

  return (
    <Container className={classes.container}>
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
          {(product !== undefined) && (
            <Grid
              container
              spacing={3}
              direction="row"
              justifyContent="flex-start"
              alignItems="stretch"
            >
              <Grid item xs={8}>
                <Card elevation={2}>
                  <CardContent>
                    <Stack
                      direction="row"
                      justifyContent="flex-start"
                      alignItems="center"
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
                          onChange={(e) => setProduct(prev => {
                            return {
                              ...prev,
                              description: e.target.value
                            }
                          })}
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
                      disabled={originalProduct?.description === product?.description}
                      onClick={handleUpdate}>
                      Update</Button>
                  </CardActions>
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
    </Container >
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
