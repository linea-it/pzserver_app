import { Container } from '@mui/material'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import ProductDetail from '../../components/ProductDetail'
import useStyles from '../../styles/pages/product'

export default function Product() {
  const classes = useStyles()
  const router = useRouter()
  const { pid } = router.query

  return (
    <Container className={classes.root}>
      {/* <Box className={classes.pageHeader}>
        <Typography variant="h6">Product</Typography>
      </Box>
      <Box component="form" noValidate autoComplete="off"> */}
      <ProductDetail internalName={pid}></ProductDetail>
      {/* </Box> */}
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
