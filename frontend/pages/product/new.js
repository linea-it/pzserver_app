import React from 'react'
import { useRouter } from 'next/router'
import { parseCookies } from 'nookies'
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
  Paper,
  Box,
  Stepper,
  Step,
  StepLabel
} from '@mui/material'
import ProductTypeSelect from '../../components/ProductTypeSelect'
import ReleaseSelect from '../../components/ReleaseSelect'
import FileUploader from '../../components/FileUploader'
import Loading from '../../components/Loading'
import useStyles from '../../styles/pages/newproduct'
import NewProductStep1 from '../../components/newProduct/Step1'
import NewProductStep2 from '../../components/newProduct/Step2'
import NewProductStep3 from '../../components/newProduct/Step3'
import NewProductStep4 from '../../components/newProduct/Step4'


export default function NewProduct() {
  const classes = useStyles()
  const router = useRouter()

  const defaultProductValues = {
    id: null,
    display_name: '',
    release: '',
    product_type: '',
    official_product: false,
    // main_file: null,
    // description_file: '',
    survey: '',
    pz_code: '',
    description: '',
    status: 0
  }
  // const [progress, setProgress] = React.useState(0)
  const [product, setProduct] = React.useState(defaultProductValues)
  const [isLoading, setLoading] = React.useState(false)
  const [activeStep, setActiveStep] = React.useState(0)

  const handleFinish = () => {
    console.log('Finish!')
  }

  const handleNextStep = record => {
    setProduct({
      ...record
    })

    setActiveStep(activeStep + 1)
  }

  const handlePrevStep = () => {
    setProduct({
      ...product
    })

    setActiveStep(activeStep - 1)
  }

  const step1 = record => {
    console.log('record: %o', record)
    return (
      <NewProductStep1
        record={record}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
      ></NewProductStep1>
    )
  }

  const step2 = record => {
    return (
      <NewProductStep2
        record={record}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
      ></NewProductStep2>
    )
  }

  const step3 = record => {
    return (
      <NewProductStep3
        record={record}
        onNext={handleNextStep}
        onPrev={handlePrevStep}
      ></NewProductStep3>
    )
  }

  const step4 = record => {
    return (
      <NewProductStep4
        record={record}
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
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      component: step1
    },
    {
      label: 'Upload Files',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      component: step2
    },
    {
      label: 'Association Columns',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      component: step3
    },
    {
      label: 'Confirm',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      component: step4
    }
  ]

  return (
    <Container className={classes.container}>
      {isLoading && <Loading isLoading={isLoading} />}
      <Box className={classes.pageHeader}>
        <Typography variant="h6">Upload Product</Typography>
      </Box>
      {/* <Stepper activeStep={activeStep}> */}
      <Stepper activeStep={activeStep} className={classes.stepper}>
        {steps.map((step, index) => {
          return (
            <Step key={step.label}>
              <StepLabel>{step.label}</StepLabel>
            </Step>
          )
        })}
      </Stepper>
      <Box className={classes.stepDescription}>
        <Typography variant="body">{steps[activeStep].description}</Typography>
      </Box>
      {product && steps[activeStep].component(product)}
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
