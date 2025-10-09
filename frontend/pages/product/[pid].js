import { Container } from '@mui/material'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import ProductDetail from '../../components/ProductDetail'
import useStyles from '../../styles/pages/product'
import { buildLoginUrl } from '../../utils/redirect'

export default function Product() {
  const classes = useStyles()
  const router = useRouter()
  const { pid } = router.query

  const isNumeric = pid && /^\d+$/.test(pid)

  return (
    <Container className={classes.root}>
      {/* <Box className={classes.pageHeader}>
        <Typography variant="h6">Product</Typography>
      </Box>
      <Box component="form" noValidate autoComplete="off"> */}
      {/* </Box> */}
      <ProductDetail
        productId={isNumeric ? parseInt(pid, 10) : null}
        internalName={!isNumeric ? pid : null}
      />
    </Container>
  )
}

export const getServerSideProps = async ctx => {
  const { 'pzserver.access_token': token } = parseCookies(ctx)

  // A better way to validate this is to have
  // an endpoint to verify the validity of the token:
  if (!token) {
    // Captura a URL atual para redirecionamento pós-login
    const currentUrl = ctx.resolvedUrl || ctx.req.url
    const loginUrl = buildLoginUrl(currentUrl)

    console.log(
      'Página protegida: Redirecionando para login com returnUrl:',
      currentUrl
    )
    console.log('Página protegida: URL de login:', loginUrl)
    return {
      redirect: {
        destination: loginUrl,
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
}
