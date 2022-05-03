import React, { useRef } from 'react'
import {
  Container,
  Grid,
  Typography,
  TextField,
  MenuItem,
  Button
} from '@mui/material'
import { parseCookies } from 'nookies'
import useStyles from '../styles/pages/upload'

export default function Upload() {
  const classes = useStyles()
  const typeRef = useRef('1')
  const nameRef = useRef('1')
  const releaseRef = useRef('1')
  const descriptionRef = useRef('')

  const handleBrowseMainFile = () => {
    const type = typeRef.current.value
    const name = nameRef.current.value
    const release = releaseRef.current.value
    const description = descriptionRef.current.value

    console.log({ type, name, release, description })
  }

  return (
    <Container className={classes.container}>
      <Grid container spacing={2} className={classes.gridContainer}>
        <Grid item xs={12}>
          <Typography variant="h2" component="h1" align="center">
            Upload
          </Typography>
        </Grid>
        <Grid item xs={12} md={6} className={classes.formContainer}>
          <TextField
            id="type"
            inputRef={typeRef}
            value={typeRef.current.value}
            label="Product Type"
            variant="outlined"
            select
            required
            fullWidth
          >
            <MenuItem value="1">Lorem</MenuItem>
            <MenuItem value="2">Ipsum</MenuItem>
            <MenuItem value="3">Consectetur</MenuItem>
          </TextField>
          <TextField
            id="name"
            inputRef={nameRef}
            value={nameRef.current.value}
            label="Product Name"
            variant="outlined"
            select
            required
            fullWidth
          >
            <MenuItem value="1">Lorem</MenuItem>
            <MenuItem value="2">Ipsum</MenuItem>
            <MenuItem value="3">Consectetur</MenuItem>
          </TextField>

          <TextField
            id="release"
            inputRef={releaseRef}
            value={releaseRef.current.value}
            label="LSST Data Release"
            variant="outlined"
            select
            required
            fullWidth
          >
            <MenuItem value="1">Lorem</MenuItem>
            <MenuItem value="2">Ipsum</MenuItem>
            <MenuItem value="3">Consectetur</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            id="description"
            inputRef={descriptionRef}
            value={descriptionRef.current.value}
            label="Description"
            variant="outlined"
            fullWidth
            multiline
            minRows={8}
          />
        </Grid>

        <Grid item xs={12} className={classes.buttonsContainer}>
          <Button variant="contained" color="secondary">
            Clear Form
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleBrowseMainFile}
          >
            Browse Main File
          </Button>
          <Button variant="contained" color="primary">
            Browse Description Ancillary File
          </Button>
        </Grid>
      </Grid>
    </Container>
  )
}

export const getServerSideProps = async ctx => {
  const { 'pzserver.token': token } = parseCookies(ctx)

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
