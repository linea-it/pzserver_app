import CloseIcon from '@mui/icons-material/Close'
import EditIcon from '@mui/icons-material/Edit'
import {
  Alert,
  Box,
  Button,
  FormControl,
  Stack,
  TextField,
  Typography
} from '@mui/material'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import MenuItem from '@mui/material/MenuItem'
import PropTypes from 'prop-types'
import React, { useEffect, useRef, useState } from 'react'
import { contentAssociation, getProductContents } from '../../services/product'
import Loading from '../Loading'
import axios from 'axios'

export default function NewProductStep3({ productId, onNext, onPrev }) {
  const ucds = [
    {
      name: 'ID',
      value: 'meta.id;meta.main'
    },
    {
      name: 'RA',
      value: 'pos.eq.ra;meta.main'
    },
    {
      name: 'Dec',
      value: 'pos.eq.dec;meta.main'
    },
    {
      name: 'z',
      value: 'src.redshift'
    },
    {
      name: 'z_err',
      value: 'stat.error;src.redshift'
    },
    {
      name: 'z_flag',
      value: 'stat.rank'
    },
    {
      name: 'survey',
      value: 'meta.curation'
    }
  ]

  const [productColumns, setProductColumns] = React.useState([])
  const [usedUcds, setUsedUcds] = React.useState([])
  const [isLoading, setLoading] = useState(false)
  const [formError, setFormError] = React.useState('')
  const [editableFields, setEditableFields] = useState({})
  const editFieldRefs = useRef({})

  const loadContents = React.useCallback(async () => {
    setLoading(true)
    getProductContents(productId)
      .then(res => {
        setProductColumns(res.results)
        setLoading(false)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }, [productId])

  useEffect(() => {
    loadContents()
  }, [loadContents])

  useEffect(() => {
    const useducds = []
    productColumns.forEach(row => {
      if (row.ucd !== null) {
        useducds.push(row.ucd)
      }
    })
    setUsedUcds(useducds)
  }, [productColumns])

  const handleSubmit = () => {
    onNext(productId)
  }
  const handlePrev = () => {
    onPrev(productId)
  }
  const onChangeUcd = (pc, value) => {
    if (pc.ucd === value) {
      return
    }
    // setLoading(true)
    contentAssociation(pc.id, value)
      .then(() => {
        // setLoading(false)
        loadContents(productId)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }

  const handleMouseDownPassword = event => {
    event.preventDefault()
  }

  const handleEditField = (pc, value) => {
    setEditableFields(prevState => ({
      ...prevState,
      [pc.column_name]: value
    }))
    updateAliasOnServer(pc.id, value)
  }

  const updateAliasOnServer = async (contentId, aliasValue) => {
    try {
      await axios.post('/api/update-aliases/', {
        productId: productId,
        updates: [
          {
            id: contentId,
            alias: aliasValue
          }
        ]
      });
    } catch (error) {
      console.error('Error updating alias:', error);
    }
  };

  const handleCancelEdit = pc => {
    const updatedEditableFields = { ...editableFields }
    delete updatedEditableFields[pc.column_name]
    setEditableFields(updatedEditableFields)
  }

  const createSelect = pc => {
    // Check Available Ucds and Current UCD when pc.ucd is not null
    const avoptions = []
    let currentUcd = null
    ucds.forEach(ucd => {
      if (usedUcds.indexOf(ucd.value) === -1 || ucd.value === pc.ucd) {
        avoptions.push(ucd)
      }
      if (ucd.value === pc.ucd) {
        currentUcd = ucd
      }
    })

    const isOptionSelected = pc.ucd !== null;

    return (
      <Box sx={{ display: "flex", alignItems: "center" }}>
        {isOptionSelected ? (
          <TextField
            value={currentUcd.name}
            readOnly
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => onChangeUcd(pc, null)}>
                    <CloseIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        ) : (
          <>
            {pc.column_name in editableFields ? (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  value={editableFields[pc.column_name]}
                  onChange={e => handleEditField(pc, e.target.value)}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => handleCancelEdit(pc)}>
                          <CloseIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  inputRef={ref => {
                    editFieldRefs.current[pc.column_name] = ref;
                  }}
                  autoFocus
                />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  select
                  value={pc.ucd || ''}
                  onChange={e => onChangeUcd(pc, e.target.value)}
                >
                  {avoptions.map(ucd => (
                    <MenuItem
                      key={`${pc.column_name}_${ucd.name}`}
                      value={ucd.value}
                    >
                      {ucd.name}
                    </MenuItem>
                  ))}
                </TextField>
                <IconButton
                  onClick={() => handleEditField(pc, '')}
                  onMouseDown={handleMouseDownPassword}
                >
                  <EditIcon />
                </IconButton>
              </Box>
            )}
          </>
        )}
      </Box>
    )
  }

  const createFields = pc => {
    return (
      <Stack
        direction="row"
        spacing={2}
        key={`fields_${pc.column_name}`}
        mb={2}
      >
        <FormControl>
          <TextField value={pc.column_name} />
        </FormControl>
        <FormControl>{createSelect(pc)}</FormControl>
      </Stack>
    )
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later, if the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  const handleFormError = () => {
    return (
      <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
        {formError}
      </Alert>
    )
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Typography paragraph variant="body">
        Please associate the column names of your file with those expected by
        the tool.
      </Typography>
      <Typography paragraph variant="body">
        It is okay to leave columns unassociated.
      </Typography>
      <Typography paragraph variant="body">
        Skip this step if the data is not tabular.
      </Typography>

      <Box
        component="form"
        sx={{
          '& .MuiTextField-root': { width: '25ch' }
        }}
        autoComplete="off"
      >
        {productColumns.map(pc => {
          return createFields(pc)
        })}
      </Box>
      {formError !== '' && handleFormError()}
      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handlePrev}
          sx={{ mr: 1 }}
        >
          Prev
        </Button>
        <Box sx={{ flex: '1 1 auto' }} />
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Next
        </Button>
      </Box>
    </React.Fragment>
  )
}

NewProductStep3.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}
