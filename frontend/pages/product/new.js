import {
  Alert,
  Box,
  Container,
  Snackbar,
  Step,
  StepLabel,
  Stepper,
  Typography
} from '@mui/material'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
import React from 'react'
import Loading from '../../components/Loading'
import { buildLoginUrl } from '../../utils/redirect'
import NewProductStep1 from '../../components/newProduct/Step1'
import NewProductStep2 from '../../components/newProduct/Step2'
import NewProductStep3 from '../../components/newProduct/Step3'
import NewProductStep4 from '../../components/newProduct/Step4'
import {
  deleteProduct,
  getProductPendingPublication
} from '../../services/product'
import useStyles from '../../styles/pages/newproduct'

export default function NewProduct() {
  const classes = useStyles()
  const router = useRouter()

  const [productId, setProductId] = React.useState(null)
  const [pendingProduct, setPendingProduct] = React.useState(null)
  const [isLoading, setLoading] = React.useState(false)
  const [activeStep, setActiveStep] = React.useState(0)
  const [open, setOpen] = React.useState(false)
  const [errorSnackbar, setErrorSnackbar] = React.useState({
    open: false,
    message: ''
  })

  React.useEffect(() => {
    // Procurar por produtos que foram criados mas não foram publicados ainda pelo usuario.
    setLoading(true)
    getProductPendingPublication()
      .then(res => {
        if (res.product) {
          setPendingProduct(res.product)
        }
        setLoading(false)
      })
      .catch(res => {
        setLoading(false)
        handleOpenErrorSnackbar(
          'Error loading pending product. Please try again.'
        )
      })
  }, [])

  React.useEffect(() => {
    setOpen(!!pendingProduct)
  }, [pendingProduct])

  const handleNextStep = id => {
    setProductId(id)
    setActiveStep(activeStep + 1)
  }

  const handlePrevStep = id => {
    setProductId(id)
    setActiveStep(activeStep - 1)
  }

  const handleFinish = internalName => {
    // Redirecionar para a pagina de detalhe do produto
    router.push(`/product/${encodeURIComponent(internalName)}`)
  }

  const step1 = productId => {
    return (
      <NewProductStep1
        productId={productId}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
        onDiscard={test}
      ></NewProductStep1>
    )
  }

  const step2 = productId => {
    return (
      <NewProductStep2
        productId={productId}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
      ></NewProductStep2>
    )
  }

  const step3 = productId => {
    return (
      <NewProductStep3
        productId={productId}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
      ></NewProductStep3>
    )
  }

  const step4 = productId => {
    return (
      <NewProductStep4
        productId={productId}
        onNext={handleFinish}
        onPrev={handlePrevStep}
      ></NewProductStep4>
    )
  }

  // Descrição do produto ->
  // upload dos arquivos ->
  // aguarda a ação do backend ->
  // associação das colunas ->
  // preview do registro e confirmação ->
  // publicar (liberar o produto para acesso)
  const steps = [
    {
      label: 'Basic Information',
      description:
        'Please provide the basic information about the new data product.'
    },
    {
      label: 'Upload Files',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    },
    {
      label: 'Columns Association',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    },
    {
      label: 'Confirm',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    }
  ]

  const handleDiscard = () => {
    setLoading(true)
    deleteProduct(pendingProduct.id)
      .then(res => {
        setLoading(false)
        setProductId(null)
        setPendingProduct(null)
      })
      .catch(res => {
        setLoading(false)
        handleOpenErrorSnackbar(
          'Failed to discard the pending product. Please try again.'
        )
      })
  }

  const handleContinue = () => {
    setProductId(pendingProduct.id)
    setPendingProduct(null)
  }

  const pendingProductAlert = () => {
    return (
      <Dialog open={open}>
        <DialogTitle>{'Pending product registration'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {'Do you want to proceed with product registration'}{' '}
            <strong>{pendingProduct.display_name}</strong>?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDiscard}>Discard</Button>
          <Button onClick={handleContinue}>Continue with registration</Button>
        </DialogActions>
      </Dialog>
    )
  }

  const test = product => {
    setPendingProduct(product)
  }

  const handleOpenErrorSnackbar = message => {
    setErrorSnackbar({
      open: true,
      message
    })
  }

  return (
    <Container className={classes.container}>
      {isLoading && <Loading isLoading={isLoading} />}
      {pendingProduct !== null && pendingProductAlert()}
      {pendingProduct === null && (
        <React.Fragment>
          <Box className={classes.pageHeader}>
            <Typography variant="h6">Upload Product</Typography>
          </Box>

          <Stepper activeStep={activeStep} className={classes.stepper}>
            {steps.map((step, index) => {
              return (
                <Step key={step.label}>
                  <StepLabel>{step.label}</StepLabel>
                </Step>
              )
            })}
          </Stepper>
          <Box
            sx={{
              mt: 2,
              mb: 2,
              p: 2
            }}
            alignItems="center"
            justifyContent="center"
          >
            {activeStep === 0 && step1(productId)}
            {activeStep === 1 && step2(productId)}
            {activeStep === 2 && step3(productId)}
            {activeStep === 3 && step4(productId)}
          </Box>
        </React.Fragment>
      )}
      <Snackbar
        open={errorSnackbar.open}
        autoHideDuration={6000}
        onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
      >
        <Alert
          onClose={() => setErrorSnackbar({ ...errorSnackbar, open: false })}
          severity="error"
          sx={{ width: '100%' }}
        >
          {errorSnackbar.message}
        </Alert>
      </Snackbar>
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
